"""Currency enumeration."""

from .utils import StrEnum


class Currency(StrEnum):
    """Supported currency codes."""

    CLP = "CLP"
    MXN = "MXN"
    PES = "PES"
    USD = "USD"
