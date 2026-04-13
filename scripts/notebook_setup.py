# Compatibility shim — notebooks import `from scripts.notebook_setup import setup`.
# The actual implementation lives in scripts/utils/notebook_setup.py.

from .utils.notebook_setup import (
    setup_notebook as setup,
    configure_plot_style,
    OKABE_ITO,
    OKABE_ITO_CYCLE,
)

__all__ = ['setup', 'configure_plot_style', 'OKABE_ITO', 'OKABE_ITO_CYCLE']
