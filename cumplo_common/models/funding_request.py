"""Funding request domain model with computed financial metrics."""

from decimal import Decimal
from functools import cached_property
from math import ceil

from pydantic import Field, computed_field

from cumplo_common.utils.constants import CUMPLO_BASE_URL, SIMULATION_AMOUNT

from .base_model import BaseModel
from .borrower import Borrower
from .credit import CreditType
from .currency import Currency
from .debtor import Debtor
from .simulation import Simulation
from .utils import StrEnum


class DurationUnit(StrEnum):
    """Unit for expressing a funding-request duration."""

    MONTH = "MONTH"
    DAY = "DAY"


class Duration(BaseModel):
    """Duration value with its unit for a funding request."""

    unit: DurationUnit = Field(...)
    value: int = Field(...)

    def __str__(self) -> str:
        """Return a human-readable duration string."""
        return f"{self.value} {self.unit.lower()}s"


class FundingRequest(BaseModel):
    """Full funding-request record with computed financial metrics."""

    id: int = Field(...)
    amount: int = Field(...)
    irr: Decimal = Field(...)
    score: Decimal = Field(...)
    due_date: str = Field(...)
    raised_amount: int = Field(...)
    maximum_investment: int = Field(...)
    investors: int = Field(...)
    raised_percentage: Decimal = Field(...)
    supporting_documents: list[str] = Field(default_factory=list)

    debtors: list[Debtor] = Field(default_factory=list)
    credit_type: CreditType = Field(...)
    simulation: Simulation = Field(...)
    duration: Duration = Field(...)
    borrower: Borrower = Field(...)
    currency: Currency = Field(...)

    @computed_field  # type: ignore[misc]
    @cached_property
    def installments(self) -> int:
        """Calculates the number of installments for the funding request."""
        return len(self.simulation.installments)

    @computed_field  # type: ignore[misc]
    @cached_property
    def profit_rate(self) -> Decimal:
        """Calculates the profit rate for the funding request."""
        if self.installments > 1:
            value = self.simulation.profit_rate
        else:
            value = (1 + self.irr / 100) ** Decimal(self.duration.value / 365) - 1
        return round(Decimal(value), ndigits=4)

    @computed_field  # type: ignore[misc]
    @cached_property
    def monthly_profit_rate(self) -> Decimal:
        """Calculates the monthly profit rate for the funding request."""
        value = (1 + self.irr / 100) ** Decimal(1 / 12) - 1
        return round(Decimal(value), ndigits=4)

    @computed_field  # type: ignore[misc]
    @cached_property
    def is_completed(self) -> bool:
        """Checks if the funding request is fully funded."""
        return self.raised_percentage == Decimal(1)

    @computed_field  # type: ignore[misc]
    @cached_property
    def url(self) -> str:
        """Builds the URL for the funding request."""
        return f"{CUMPLO_BASE_URL}/{self.id}"

    def monthly_profit(self, amount: int) -> int:
        """
        Calculate the monthly profit for a given amount.

        Args:
            amount (int): The amount to calculate the profit for

        Returns:
            int: The monthly profit for the given amount

        """
        return ceil(self.monthly_profit_rate * amount)

    @computed_field  # type: ignore[misc]
    @cached_property
    def upfront_fee(self) -> Decimal:
        """Calculates the upfront fee for the funding request."""
        return round(Decimal(self.simulation.upfront_fee / SIMULATION_AMOUNT), 4)

    @computed_field  # type: ignore[misc]
    @cached_property
    def exit_fee(self) -> Decimal:
        """Calculates the exit fee for the funding request."""
        return round(Decimal(self.simulation.exit_fee / SIMULATION_AMOUNT), 4)
