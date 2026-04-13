# ---
# description: |
#   Core notebook setup utility. Configures matplotlib with publication-quality
#   RC params and the Okabe-Ito 8-color colorblind-safe palette, enables
#   autoreload, and returns common library handles.
# entry_point: from scripts.utils import setup_notebook; PROJECT_ROOT, np, pd, plt, Path = setup_notebook()
# dependencies:
#   - matplotlib
#   - numpy
#   - pandas
#   - IPython (optional, for autoreload)
# input: |
#   No CLI arguments. Called from Jupyter notebooks. Automatically locates
#   project root by searching for a 'scripts' directory in the path hierarchy.
# process: |
#   Enables IPython autoreload, imports scientific libraries, sets matplotlib
#   RC params (Okabe-Ito 8-color palette, large fonts, thick spines/ticks),
#   and resolves the project root path.
# output: |
#   Returns (PROJECT_ROOT, np, pd, plt, Path). Side effect: matplotlib global
#   RC params are updated for all subsequent plots in the session.
# last_updated: 2026-04-09
# ---

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Okabe & Ito (2008) colorblind-safe palette — 8 colors
# Source: Okabe, M. & Ito, K. (2008). Color Universal Design (CUD).
#         https://jfly.uni-koeln.de/color/
# ---------------------------------------------------------------------------
OKABE_ITO = {
    'orange':         '#E69F00',
    'sky_blue':       '#56B4E9',
    'bluish_green':   '#009E73',
    'yellow':         '#F0E442',
    'blue':           '#0072B2',
    'vermillion':     '#D55E00',
    'reddish_purple': '#CC79A7',
    'black':          '#000000',
}

# Ordered list for matplotlib prop_cycle (yellow last — low contrast on white)
OKABE_ITO_CYCLE = [
    '#E69F00',  # orange
    '#56B4E9',  # sky blue
    '#009E73',  # bluish green
    '#0072B2',  # blue
    '#D55E00',  # vermillion
    '#CC79A7',  # reddish purple
    '#F0E442',  # yellow
    '#000000',  # black
]


def setup_notebook():
    """
    Set up notebook environment.

    1. Enables IPython autoreload
    2. Imports and returns common scientific libraries
    3. Configures matplotlib for publication-quality plots
    4. Resolves and returns project root path

    Returns:
        tuple: (PROJECT_ROOT, np, pd, plt, Path)

    Usage:
        from scripts.utils import setup_notebook
        PROJECT_ROOT, np, pd, plt, Path = setup_notebook()
    """
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic('load_ext', 'autoreload')
            ipython.run_line_magic('autoreload', '2')
            print("[OK] Autoreload enabled")
    except Exception as e:
        print(f"[WARNING] Could not enable autoreload: {e}")

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    PROJECT_ROOT = _find_project_root()
    configure_plot_style()
    print("[OK] Matplotlib configured (Okabe-Ito palette, publication style)")
    print("=" * 50)
    print("Setup complete!")
    print("=" * 50)

    return PROJECT_ROOT, np, pd, plt, Path


def _find_project_root():
    try:
        import scripts
        if hasattr(scripts, '__file__') and scripts.__file__ is not None:
            root = Path(scripts.__file__).parent.parent
            print(f"[OK] Project root (installed package): {root}")
            return root
    except ImportError:
        pass

    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / 'scripts').exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            print(f"[OK] Project root (path search): {parent}")
            return parent

    raise RuntimeError("Could not find project root (no 'scripts' directory found)")


def configure_plot_style():
    """Configure matplotlib RC params for publication-quality, colorblind-safe plots."""
    import matplotlib as mpl

    mpl.rcParams.update({
        # Figure
        'figure.dpi':          150,
        'savefig.dpi':         600,
        'figure.figsize':      (10, 7),
        'figure.facecolor':    'white',
        'savefig.facecolor':   'white',
        'savefig.bbox':        'tight',
        'savefig.pad_inches':  0.1,
        'savefig.format':      'png',

        # Font — STIX Two (serif, Times-like, full LaTeX math support)
        'font.family':         'STIXGeneral',
        'mathtext.fontset':    'stix',
        'font.size':           16,
        'axes.labelsize':      22,
        'axes.titlesize':      22,
        'xtick.labelsize':     18,
        'ytick.labelsize':     18,
        'legend.fontsize':     18,
        'legend.title_fontsize': 18,

        # Axes
        'axes.linewidth':      2,
        'axes.edgecolor':      'black',
        'axes.labelcolor':     'black',
        'axes.grid':           False,

        # Ticks — all four sides, inward (physics convention)
        'xtick.major.width':   2,    'ytick.major.width':   2,
        'xtick.minor.width':   1.5,  'ytick.minor.width':   1.5,
        'xtick.major.size':    6,    'ytick.major.size':    6,
        'xtick.minor.size':    4,    'ytick.minor.size':    4,
        'xtick.direction':     'in', 'ytick.direction':     'in',
        'xtick.top':           True, 'xtick.bottom':        True,
        'ytick.left':          True, 'ytick.right':         True,

        # Lines
        'lines.linewidth':     2,
        'lines.markersize':    7,

        # Legend
        'legend.frameon':      True,
        'legend.framealpha':   0.9,
        'legend.edgecolor':    '0.8',
        'legend.fancybox':     False,

        # Okabe-Ito color cycle + viridis colormap
        'axes.prop_cycle':     mpl.cycler(color=OKABE_ITO_CYCLE),
        'image.cmap':          'viridis',
    })


__all__ = ['setup_notebook', 'configure_plot_style', 'OKABE_ITO', 'OKABE_ITO_CYCLE']
