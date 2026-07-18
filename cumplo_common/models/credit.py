"""Credit type enumeration."""

from .utils import StrEnum


class CreditType(StrEnum):
    """Supported credit types for funding requests."""

    HUD_SUBSIDY = "HOUSING & URBAN DEVELOPMENT SUBSIDY"
    TREASURY_SUBSIDY = "TREASURY SUBSIDY"
    WORKING_CAPITAL = "WORKING CAPITAL"
    FACTORING = "FACTORING"
