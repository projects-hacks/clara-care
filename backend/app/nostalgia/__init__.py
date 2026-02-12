"""
Nostalgia Mode Module
Provides era-specific content to engage elderly patients
"""

from .era import calculate_golden_years, get_era_label, get_decade_from_year
from .youcom_client import YouComClient

__all__ = [
    "calculate_golden_years",
    "get_era_label",
    "get_decade_from_year",
    "YouComClient"
]
