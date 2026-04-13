# EB in FGT/O-FGT/CrPS4 Data Analysis Project

## Project Overview
This project analyses exchange bias (EB) in van der Waals heterostructures composed of Fe₃GaTe₂ (FGT), oxidised FGT (O-FGT), and CrPS₄. Transport measurements (Hall and longitudinal resistance) were performed in a cryostat across a range of temperatures and applied magnetic fields, including field-cooling and pre-field protocols, to characterise the EB field, coercivity, and their temperature dependence.

## Architecture & Design Principles

### Modular Pipeline Approach
Break analysis into discrete, focused scripts. Notebooks orchestrate and visualise; scripts compute.

### Key Rules
1. **Small, focused scripts**: Each script < 200 lines, one analysis step only.
2. **Every script has YAML front matter** (see template below).
3. **Light data readers**: Simple classes in `data_loader.py` for I/O only — handles both `.h5` (HDF5) and `.txt` files.
4. **Notebook as orchestrator**: Notebooks call scripts and plot results.
5. **Output discipline**: Results → `output/`, publication figures → `figures/`, temp files → `tmp/`.

### Script YAML Front Matter (required on every script)
```python
# ---
# description: |
#   (2-3 sentences) What this script does and why it exists.
# entry_point: python script_name.py [args]
# dependencies:
#   - package_name >= version
# input: |
#   (2-3 sentences) What it needs: files, CLI args, env vars.
# process: |
#   (2-3 sentences) Core logic flow.
# output: |
#   (2-3 sentences) Files, stdout, or side effects produced.
# last_updated: YYYY-MM-DD
# ---
```

## Project Structure

```
EB in FGT-OFGT_CrPS4/
├── data/                   # Raw data (copied from CrPs4/Exchange Bias/)
│   ├── Device2/            # Earlier device measurements
│   └── Device4/            # Later device measurements (FGT-CPS-hBN stack)
│   └── Rebuttal_FGT_CPS/   # Rebuttal-stage measurements (OFGT, FC at 10K)
├── output/                 # Analysis outputs (CSVs, intermediate results)
├── figures/                # Publication-ready figures
├── tmp/                    # Temporary/intermediate files
├── raw_scripts/            # Original analysis scripts (reference only)
├── scripts/                # Installable Python package (pip install -e .)
│   ├── __init__.py
│   ├── data_loader.py      # Reads .h5 and .txt measurement files
│   ├── step1_*.py          # Analysis steps
│   └── utils/
│       ├── __init__.py
│       └── notebook_setup.py
└── notebooks/
    └── *.ipynb
```

## Data
Raw data lives in `data/` and mirrors the original folder layout from `CrPs4/Exchange Bias/` on OneDrive. Data files are `.h5` (HDF5, from the PPMS/cryostat) and `.txt`. **Do not modify files in `data/`.**

Key measurement types:
- **Field-cooled (FC)**: sample cooled in ±8 T field; exchange bias measured at base temperature
- **Pre-field (PF)**: field applied at base temperature before hysteresis loop; ±1–2 T
- **Temperature dependence**: EB field vs temperature sweeps
- **Training effect**: coercivity/EB vs loop cycle number

## Install

```bash
pip install -e .
```
