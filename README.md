# Harnessing Van der Waals CrPS₄ and Surface Oxides for Nonmonotonic Preset Field Induced Exchange Bias in Fe₃GeTe₂

**Puthirath Balan, A. et al.**, *ACS Nano* **18**, 8383–8391 (2024).
DOI: [10.1021/acsnano.3c13034](https://doi.org/10.1021/acsnano.3c13034)

---

## Overview

This repository contains the transport measurement data and Python analysis code supporting the above paper. The study characterises exchange bias (EB) in van der Waals heterostructures composed of Fe₃GeTe₂ (FGT), oxidised FGT (O-FGT), and CrPS₄. Hall and longitudinal resistance were measured across a range of temperatures and applied magnetic fields using field-cooling and preset-field protocols to quantify the EB field, coercivity, and their temperature dependence.

---

## Repository structure

```
.
├── data/                          # Raw measurement data (.h5 and .txt)
│   ├── Device2/                   # Earlier device measurements (12 T cryostat)
│   ├── Device4/                   # Later device measurements (FGT–CrPS₄–hBN stack)
│   └── Rebuttal_FGT_CPS/          # Rebuttal-stage measurements (O-FGT, FC at 10 K)
├── notebooks/                     # Analysis notebooks (one per measurement type)
├── scripts/                       # Installable Python package
│   ├── data_loader.py             # Readers for .h5 and .txt measurement files
│   └── notebook_setup.py         # Shared notebook initialisation
├── pyproject.toml
├── requirements.txt
├── CITATION.cff
├── LICENSE
└── LICENSE-DATA
```

---

## Installation

```bash
pip install -e .
```

Or, using only `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Usage

Open any notebook in `notebooks/` with JupyterLab or VS Code. Each notebook is self-contained and loads data relative to the project root — no path configuration is needed after installation.

---

## Data formats

| Format | Reader function | Description |
|--------|----------------|-------------|
| `.h5` (HDF5) | `load_h5(path)` | PPMS/cryostat output; contains field, temperature, and resistance channels |
| `.txt` | `load_txt(path, skiprows, vxy_col)` | Tab-delimited export from the measurement software |

Both readers return a dict with keys `Field`, `Vxy`, `Vxx`, `Vxy_err`, `Vxx_err`, `T`.

---

## Citation

If you use this code or data, please cite:

```bibtex
@article{doi:10.1021/acsnano.3c13034,
  author  = {Puthirath Balan, Aravind and Kumar, Aditya and Scholz, Tanja
             and Lin, Zhongchong and Shahee, Aga and Fu, Shuai
             and Denneulin, Thibaud and Vas, Joseph and Kov{\'a}cs, Andr{\'a}s
             and Dunin-Borkowski, Rafal E. and Wang, Hai I. and Yang, Jinbo
             and Lotsch, Bettina V. and Nowak, Ulrich and Kl{\"a}ui, Mathias},
  title   = {Harnessing Van der Waals {CrPS4} and Surface Oxides for
             Nonmonotonic Preset Field Induced Exchange Bias in {Fe3GeTe2}},
  journal = {ACS Nano},
  volume  = {18},
  number  = {11},
  pages   = {8383--8391},
  year    = {2024},
  doi     = {10.1021/acsnano.3c13034},
}
```

---

## License

| Component | License |
|-----------|---------|
| Code (`notebooks/`, `scripts/`, `*.py`, `*.toml`) | [MIT License](LICENSE) |
| Data (`data/`) | [CC BY 4.0](LICENSE-DATA) |

**Data reuse requires attribution.** Any work that uses the data in `data/` must cite the paper:

> Puthirath Balan, A.; Kumar, A.; Scholz, T.; Lin, Z.; Shahee, A.; Fu, S.; Denneulin, T.; Vas, J.; Kovács, A.; Dunin-Borkowski, R. E.; Wang, H. I.; Yang, J.; Lotsch, B. V.; Nowak, U.; Kläui, M. "Harnessing Van der Waals CrPS₄ and Surface Oxides for Nonmonotonic Preset Field Induced Exchange Bias in Fe₃GeTe₂." *ACS Nano* **18**, 8383–8391 (2024). DOI: [10.1021/acsnano.3c13034](https://doi.org/10.1021/acsnano.3c13034)
