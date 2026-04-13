"""
EB in FGT/O-FGT/CrPS4 analysis scripts.
Modular data loaders and analysis tools for exchange bias transport measurements.
"""

from .data_loader import (
    load_h5, load_txt, load_folder, get_file_list,
    offset_and_AHE, normalize,
    coercivity, coercivity_zero_crossing, coercivity_largest_jump,
    exchange_bias, coercive_width,
    fixjump, fix_field,
    sort_serial,
    sweeps_separate, sym_asym,
)

__all__ = [
    'load_h5', 'load_txt', 'load_folder', 'get_file_list',
    'offset_and_AHE', 'normalize',
    'coercivity', 'coercivity_zero_crossing', 'coercivity_largest_jump',
    'exchange_bias', 'coercive_width',
    'fixjump', 'fix_field',
    'sort_serial',
    'sweeps_separate', 'sym_asym',
]

__version__ = "0.1.0"
