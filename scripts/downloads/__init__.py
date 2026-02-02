"""Downloads package for string matchers."""

from .download_fdr import download_fdr
from .download_dfc import download_dfc
from .download_ac import download_ac
from .download_dataset import download_dataset

__all__ = [
    'download_fdr',
    'download_dfc',
    'download_ac',
    'download_dataset',
]
