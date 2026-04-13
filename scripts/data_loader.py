# ---
# description: |
#   Data loading and analysis utilities for FGT/O-FGT/CrPS4 exchange bias
#   transport measurements. Provides two plain loaders (HDF5 and TSV) plus
#   shared analysis helpers (coercivity, AHE amplitude, jump correction, field
#   polarity repair, symmetric/antisymmetric decomposition) used across all notebooks.
# entry_point: from scripts.data_loader import load_h5, load_txt, coercivity_zero_crossing, offset_and_AHE
# dependencies:
#   - numpy
#   - pandas
#   - h5py
#   - scipy
#   - matplotlib
# input: |
#   HDF5 files from the home-built cryostat (Device2) or tab-delimited .txt
#   files from the 12T cryostat (Device4 / Rebuttal measurements).
# output: |
#   Each loader returns a plain dict with keys: Field (mT), Vxy (uV), Vxx (uV),
#   Vxy_err (uV), Vxx_err (uV), T (K), VTIT (K). Analysis helpers return
#   numpy scalars/arrays.
# last_updated: 2026-04-12  (added P=None auto-detection to load_h5)
# ---

from pathlib import Path
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# HDF5 loader  (Device2 — home-built cryostat)
# ---------------------------------------------------------------------------

def load_h5(filepath, channel_xy=2, P=1):
    """
    Load a home-built cryostat HDF5 file.

    The instrument records 2*P raw voltage samples per field step (P with
    positive current, P with negative current) to cancel offsets. This function
    averages them and converts units.

    Parameters
    ----------
    filepath : str or Path
    channel_xy : int, 1 or 2
        HP34420A channel wired to the Hall (Rxy) contacts. Default 2.
        Use 1 for OFGT/CPS samples where the wiring was reversed.
    P : int or None
        Raw samples per current polarity per field step. Default 1.
        Pass ``None`` to auto-detect P from the raw field array (Script 10
        method: count consecutive near-identical field points, P ≈ count/2).

    Returns
    -------
    dict with keys:
        Field   : np.ndarray  field in mT
        Vxy     : np.ndarray  Hall voltage in uV
        Vxx     : np.ndarray  longitudinal voltage in uV
        Vxy_err : np.ndarray  std-dev error bar on Vxy in uV
        Vxx_err : np.ndarray  std-dev error bar on Vxx in uV
        T       : float       mean sample temperature in K
        VTIT    : float       mean VTI temperature in K
    """
    import h5py
    ch_xy  = f'Avg_Voltage_Hp34420A_Ch{channel_xy}'
    ch_xx  = f'Avg_Voltage_Hp34420A_Ch{3 - channel_xy}'
    raw_xy = f'Voltage_Array_Hp34420A_Ch{channel_xy}'
    raw_xx = f'Voltage_Array_Hp34420A_Ch{3 - channel_xy}'

    with h5py.File(filepath) as f:
        Field_raw = np.array(f['Data']['Magnetic_Field'],   dtype=float)
        Sig_raw   = np.array(f['Data'][ch_xy],              dtype=float)
        Rxx_raw   = np.array(f['Data'][ch_xx],              dtype=float)
        rawS      = np.array(f['Data'][raw_xy],             dtype=float)
        rawR      = np.array(f['Data'][raw_xx],             dtype=float)
        ST_arr    = np.array(f['Data']['Rod_Temp'],         dtype=float)
        VTIT_arr  = np.array(f['Data']['VTI_Temp'],         dtype=float)

    if P is None:
        # Auto-detect P from raw field array: count how many consecutive field
        # values are nearly identical (threshold 0.005 in instrument units).
        # The instrument stores 2*P samples per field step, so P = count/2.
        i = 0
        while i < len(Field_raw) - 1 and abs(Field_raw[i] - Field_raw[i + 1]) < 0.005:
            i += 1
        P = max(1, round((i + 1) / 2))

    P2 = 2 * P
    n  = len(Field_raw) // P2
    F, Sig, Ref, Serr, Rerr = [], [], [], [], []
    for i in range(0, n * P2, P2):
        F.append(   np.mean(Field_raw[i:i+P2]))
        Sig.append( np.mean(np.abs(Sig_raw[i:i+P2])))
        Ref.append( np.mean(np.abs(Rxx_raw[i:i+P2])))
        t = np.abs(rawS[i:i+P]) + np.abs(rawS[i+P:i+P2])
        Serr.append(np.std(t))
        t = np.abs(rawR[i:i+P]) + np.abs(rawR[i+P:i+P2])
        Rerr.append(np.std(t))

    Field = np.array(F)    * 8000 / 93.17   # instrument units → mT
    Vxy   = np.array(Sig)  * 1e6            # V → uV
    Vxx   = np.array(Ref)  * 1e6
    Verr  = np.array(Serr) * 1e6
    Rerr  = np.array(Rerr) * 1e6
    T     = round(float(np.mean(ST_arr)))
    VTIT  = float(np.mean(VTIT_arr))

    return dict(Field=Field, Vxy=Vxy, Vxx=Vxx,
                Vxy_err=Verr, Vxx_err=Rerr, T=T, VTIT=VTIT)


# ---------------------------------------------------------------------------
# TSV loader  (Device4 and Rebuttal — 12T / Quantum Design cryostat)
# ---------------------------------------------------------------------------

def load_txt(filepath, skiprows=16, vxy_col='Voltage-1(V)', trim='tail'):
    """
    Load a tab-delimited measurement file from the 12T cryostat.

    Column names baked into the instrument headers:
        'Magnetic Field (T)', 'Voltage-1(V)', 'Voltage-2 (V)',
        'Std. of V1', 'Std. of V2',
        'VTI Temperature (K)', 'Sample Temparture (K)'   <- typo is in the file

    Parameters
    ----------
    filepath : str or Path
    skiprows : int
        Header lines to skip before the column-name row. Default 16.
        Use 15 for older Device2 12T files.
    vxy_col : str
        Column name for the Hall voltage channel. Default 'Voltage-1(V)'.
        Use 'Voltage-2 (V)' for Device2 pre-field and critical-field files
        where V2 = Rxy.
    trim : str or None
        'tail'  — drop last 2 rows (instrument artefact, Device4 files)
        'head'  — drop first row (Device2 12T files)
        None    — no trimming

    Returns
    -------
    Same dict format as load_h5.
    """
    vxx_col = 'Voltage-2 (V)' if vxy_col == 'Voltage-1(V)' else 'Voltage-1(V)'
    err_xy  = 'Std. of V1'    if vxy_col == 'Voltage-1(V)' else 'Std. of V2'
    err_xx  = 'Std. of V2'    if vxy_col == 'Voltage-1(V)' else 'Std. of V1'

    df = pd.read_csv(filepath, delimiter='\t', skiprows=skiprows)
    if trim == 'tail':
        df = df.iloc[:-2, :]
    elif trim == 'head':
        df = df.iloc[1:, :]

    Field = df['Magnetic Field (T)'].to_numpy(dtype=float) * 1000   # T → mT
    Vxy   = df[vxy_col].to_numpy(dtype=float)             * 1e6     # V → uV
    Vxx   = df[vxx_col].to_numpy(dtype=float)             * 1e6
    Verr  = df[err_xy].to_numpy(dtype=float)              * 1e6
    Rerr  = df[err_xx].to_numpy(dtype=float)              * 1e6
    T     = round(float(np.mean(df['Sample Temparture (K)'].to_numpy(dtype=float))))
    VTIT  = float(np.mean(df['VTI Temperature (K)'].to_numpy(dtype=float)))

    return dict(Field=Field, Vxy=Vxy, Vxx=Vxx,
                Vxy_err=Verr, Vxx_err=Rerr, T=T, VTIT=VTIT)


def load_folder(folder, ext=('.h5', '.txt'), **kwargs):
    """
    Load all matching files in a folder (non-recursive).
    Extra kwargs are forwarded to load_h5 or load_txt as appropriate.
    Returns list of (filename, data_dict).
    """
    folder = Path(folder)
    results = []
    for fp in sorted(folder.iterdir()):
        if fp.suffix.lower() in ext:
            try:
                if fp.suffix.lower() == '.h5':
                    d = load_h5(fp, **{k: v for k, v in kwargs.items()
                                       if k in ('channel_xy', 'P')})
                else:
                    d = load_txt(fp, **{k: v for k, v in kwargs.items()
                                        if k in ('skiprows', 'vxy_col', 'trim')})
                results.append((fp.name, d))
            except Exception as e:
                print(f'[WARNING] {fp.name}: {e}')
    return results


# ---------------------------------------------------------------------------
# Analysis utilities  (shared across all notebooks)
# ---------------------------------------------------------------------------

def _constfit(values):
    """Fit a constant to an array; return (value, std_error)."""
    from scipy.optimize import curve_fit
    x = np.linspace(0, 1, len(values))
    popt, pcov = curve_fit(lambda x, a: a, x, values)
    return float(popt[0]), float(np.sqrt(np.diag(pcov))[0])


def offset_and_AHE(V):
    """
    Estimate the Hall offset and AHE amplitude of a hysteresis loop by
    fitting a constant to each saturation branch (iterated twice for robustness).

    Returns
    -------
    offset, offset_err, Vahe, Vahe_err  — all in the same units as V
    """
    V = np.asarray(V, dtype=float)
    mean = np.mean(V)
    for _ in range(2):
        Vup = V[V > mean]
        Vdn = V[V <= mean]
        Vmax, Vmax_err = _constfit(Vup)
        Vmin, Vmin_err = _constfit(Vdn)
        offset = (Vmax + Vmin) / 2
        Vahe   = (Vmax - Vmin) / 2
        Vahe_err   = Vmax_err + Vmin_err
        offset_err = Vmax_err + Vmin_err
        # Narrow to ±10σ around each plateau for second pass
        Vup = V[np.abs(V - Vmax) < 10 * Vahe_err]
        Vdn = V[np.abs(V - Vmin) < 10 * Vahe_err]
        if len(Vup) > 1 and len(Vdn) > 1:
            Vmax, Vmax_err = _constfit(Vup)
            Vmin, Vmin_err = _constfit(Vdn)
            offset     = (Vmax + Vmin) / 2
            offset_err = Vmax_err + Vmin_err
            Vahe       = (Vmax - Vmin) / 2
            Vahe_err   = Vmax_err + Vmin_err
    return offset, offset_err, Vahe, Vahe_err


def normalize(V, offset, Vahe):
    """Return (V - offset) / Vahe."""
    return (np.asarray(V, dtype=float) - offset) / Vahe


def coercivity(F, normsig):
    """
    Find coercive fields H_C1 (negative branch) and H_C2 (positive branch)
    by linear interpolation through the zero crossings of a normalised loop.

    Parameters
    ----------
    F       : array-like  field in any consistent unit
    normsig : array-like  normalised signal (zero crossings at coercive fields)

    Returns
    -------
    HC_neg, HC_pos : floats
    """
    F, S = np.asarray(F, dtype=float), np.asarray(normsig, dtype=float)
    crossings = []
    for i in range(len(F) - 1):
        if S[i] * S[i + 1] < 0:
            # linear interpolation
            H = (F[i] * S[i+1] - F[i+1] * S[i]) / (S[i+1] - S[i])
            crossings.append(H)
    if len(crossings) < 2:
        return np.nan, np.nan
    if crossings[0] < 0:
        return crossings[0], crossings[1]
    return crossings[1], crossings[0]


def exchange_bias(HC_neg, HC_pos):
    """H_EB = (H_C1 + H_C2) / 2"""
    return (HC_neg + HC_pos) / 2


def coercive_width(HC_neg, HC_pos):
    """H_C = |H_C1 - H_C2| / 2"""
    return abs(HC_neg - HC_pos) / 2


# Explicit alias so notebooks can be unambiguous about which method they use.
coercivity_zero_crossing = coercivity


def coercivity_largest_jump(F, Sig):
    """
    Find coercive fields by locating the largest |ΔSig| step in each
    half-sweep of the raw (un-normalised) signal.

    Used exclusively in ``All field cooling EB.py`` (Script 5).  All other
    scripts use ``coercivity_zero_crossing``.

    Parameters
    ----------
    F   : array-like  field in mT (full sweep)
    Sig : array-like  raw Hall signal in µV (full sweep, NOT normalised)

    Returns
    -------
    HC_neg, HC_pos : floats  coercive fields in the same units as F
    """
    F, Sig = np.asarray(F, dtype=float), np.asarray(Sig, dtype=float)
    half = len(F) // 2

    CP = 0.0
    last = 0.0
    for i in range(half - 1):
        jump = abs(Sig[i + 1] - Sig[i])
        if jump > last:
            last = jump
            CP = (F[i] + F[i + 1]) / 2

    CN = 0.0
    last = 0.0
    for i in range(half - 1):
        j = i + half
        jump = abs(Sig[j + 1] - Sig[j])
        if jump > last:
            last = jump
            CN = (F[j] + F[j + 1]) / 2

    return CN, CP


# ---------------------------------------------------------------------------
# Signal correction utilities
# ---------------------------------------------------------------------------

def fixjump(V, guessjump, guessindex=None):
    """
    Correct a single voltage step-discontinuity ('jump') in a sweep.

    Finds the first index where |V[i+1] - V[i]| > guessjump and shifts all
    points *before* that index by the jump magnitude to remove it.

    Parameters
    ----------
    V          : np.ndarray  voltage array (modified in-place and returned)
    guessjump  : float       threshold above which a step is considered a jump
    guessindex : int or None
        If given, start scanning from index ``guessindex - 1`` (as in the
        FC_P8T script where the jump is known to occur near a specific index).
        If None (default), scan from the beginning.

    Returns
    -------
    V : np.ndarray  (same array, corrected in-place)
    """
    V = np.asarray(V, dtype=float).copy()
    start = max(0, (guessindex - 1) if guessindex is not None else 0)
    n = len(V) - 1 - (guessindex if guessindex is not None else 0)
    jump1 = 0.0
    cut = len(V)
    for k in range(n):
        i = k + start
        if abs(V[i + 1] - V[i]) > guessjump:
            jump1 = V[i + 1] - V[i]
            cut = i + 1
            break
    V[:cut] = V[:cut] + jump1
    return V


def fix_field(F_arr, n):
    """
    Correct isolated field-polarity sign errors caused by power-supply glitches.

    Iterates ``n`` times over the field array and flips the sign of any point
    that has opposite sign to both its neighbours (i.e. it is a single-point
    polarity outlier).

    Used in ``OFGT_PF_PM2T_10102023.py`` only.

    Parameters
    ----------
    F_arr : np.ndarray  field array (modified in-place and returned)
    n     : int         number of correction passes (use 5 for OFGT PF data)

    Returns
    -------
    F_arr : np.ndarray
    """
    F_arr = np.asarray(F_arr, dtype=float).copy()
    for _ in range(n):
        for i in range(len(F_arr) - 2):
            if F_arr[i] * F_arr[i + 1] < 0 and F_arr[i + 1] * F_arr[i + 2] < 0:
                F_arr[i + 1] *= -1
    return F_arr


# ---------------------------------------------------------------------------
# Sorting utilities
# ---------------------------------------------------------------------------

def sort_serial(serial_numbers, data):
    """
    Sort a list of data objects by their associated serial_numbers (temperatures).

    Parameters
    ----------
    serial_numbers : list  sortable keys (e.g. temperature floats)
    data           : list  parallel list of data objects

    Returns
    -------
    sorted_data : list  reordered by ascending serial_numbers
    """
    indices = {serial_numbers[i]: i for i in range(len(serial_numbers))}
    sorted_keys = sorted(serial_numbers)
    return [data[indices[k]] for k in sorted_keys]


def get_file_list(folder, ext=('.h5', '.txt')):
    """
    Return sorted list of Path objects in *folder* matching *ext*.

    Parameters
    ----------
    folder : str or Path
    ext    : tuple of str  extensions to include (lower-cased comparison)

    Returns
    -------
    list of Path
    """
    folder = Path(folder)
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in ext)


# ---------------------------------------------------------------------------
# Symmetric / antisymmetric decomposition  (OFGT notebook only)
# ---------------------------------------------------------------------------

def sweeps_separate(F, V):
    """
    Split a full hysteresis sweep into two half-sweeps at the field turning point.

    Also generates a diagnostic figure of the full sweep (matches original
    script behaviour — intermediate analysis figure).

    Parameters
    ----------
    F, V : array-like  full-sweep field and signal

    Returns
    -------
    V_1, V_2 : np.ndarray  first and second half-sweeps of V
    """
    import matplotlib.pyplot as plt
    F = np.asarray(F, dtype=float)
    V = np.asarray(V, dtype=float)
    plt.figure()
    plt.plot(F, V)
    F_r = [round(x, 3) for x in F.tolist()]
    max_abs = np.max(np.abs(F_r))
    mid = np.where(np.abs(F_r) == max_abs)[0][1]
    V_1 = V[:mid + 1]
    if F_r[mid] == F_r[mid + 1]:
        V_2 = V[mid + 1:]
    else:
        V_2 = V[mid:]
    return V_1, V_2


def sym_asym(F, V):
    """
    Decompose a hysteresis loop into its symmetric and antisymmetric components.

    Generates three intermediate figures (one from sweeps_separate, two from
    this function) matching the original script behaviour.

    Parameters
    ----------
    F, V : array-like  full-sweep field and signal

    Returns
    -------
    symV, asymV : np.ndarray  symmetric and antisymmetric parts of V
    """
    import matplotlib.pyplot as plt
    F = np.asarray(F, dtype=float)
    V = np.asarray(V, dtype=float)
    F_1, F_2 = sweeps_separate(F, F)
    V_1, V_2 = sweeps_separate(F, V)

    plt.figure()
    plt.plot(F_1, V_1)
    plt.figure()
    plt.plot(F_2, V_2)

    sym_1  = np.array([(V_1[i] + V_1[len(V_1) - i - 1]) / 2 for i in range(len(V_1))])
    asym_1 = np.array([(V_1[i] - V_1[len(V_1) - i - 1]) / 2 for i in range(len(V_1))])
    sym_2  = np.array([(V_2[i] + V_2[len(V_2) - i - 1]) / 2 for i in range(len(V_2))])
    asym_2 = np.array([(V_2[i] - V_2[len(V_2) - i - 1]) / 2 for i in range(len(V_2))])

    return np.concatenate((sym_1, sym_2)), np.concatenate((asym_1, asym_2))


__all__ = [
    'load_h5', 'load_txt', 'load_folder', 'get_file_list',
    'offset_and_AHE', 'normalize',
    'coercivity', 'coercivity_zero_crossing', 'coercivity_largest_jump',
    'exchange_bias', 'coercive_width',
    'fixjump', 'fix_field',
    'sort_serial',
    'sweeps_separate', 'sym_asym',
]
