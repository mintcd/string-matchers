"""Downloads package for string matchers."""

from .fdr_download import download_fdr
from .dfc_download import download_dfc
from .ac_download import download_ac
from .main import download_rulesets, extract_patterns

__all__ = [
    'download_fdr',
    'download_dfc',
    'download_ac',
    'download_rulesets',
    'extract_patterns',
]
