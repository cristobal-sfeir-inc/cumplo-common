"""Portfolio domain models with grouped category breakdowns."""

from decimal import Decimal
from functools import cached_property

from pydantic import Field, computed_field

from .base_model import BaseModel
from .utils import StrEnum


class PortfolioCategory(StrEnum):
    """Categories of the funding requests in the portfolio."""

    PAID = "paid"
    TOTAL = "total"
    CURED = "cured"
    ACTIVE = "active"
    OVERDUE = "overdue"
    ON_TIME = "on_time"
    DELINQUENT = "delinquent"
    OUTSTANDING = "outstanding"


class PortfolioCategoryUnit(StrEnum):
    """Units used for representing a category of funding requests in a portfolio."""

    PERCENTAGE = "percentage"
    AMOUNT = "amount"
    COUNT = "count"


class PortfolioGroup(BaseModel):
    """Group of funding requests of a portfolio in the same category."""

    amount: Decimal = Field(...)
    count: int = Field(...)

    def get(self, unit: PortfolioCategoryUnit) -> Decimal:
        """Get the value of the group in the given unit."""
        return getattr(self, unit.value)


class Portfolio(BaseModel):
    """Aggregated portfolio breakdown by category."""

    cured: PortfolioGroup = Field(...)
    active: PortfolioGroup = Field(...)
    overdue: PortfolioGroup = Field(...)
    on_time: PortfolioGroup = Field(...)
    delinquent: PortfolioGroup = Field(...)

    @computed_field  # type: ignore[misc]
    @cached_property
    def total(self) -> PortfolioGroup:
        """Total is the sum of outstanding and paid."""
        return PortfolioGroup(
            amount=self.outstanding.amount + self.paid.amount,
            count=self.outstanding.count + self.paid.count,
        )

    @computed_field  # type: ignore[misc]
    @cached_property
    def outstanding(self) -> PortfolioGroup:
        """Outstanding is the sum of active, overdue and delinquent."""
        return PortfolioGroup(
            amount=self.active.amount + self.overdue.amount + self.delinquent.amount,
            count=self.active.count + self.overdue.count + self.delinquent.count,
        )

    @computed_field  # type: ignore[misc]
    @cached_property
    def paid(self) -> PortfolioGroup:
        """Paid is the sum of credits paid on time and cured."""
        return PortfolioGroup(
            amount=self.on_time.amount + self.cured.amount,
            count=self.on_time.count + self.cured.count,
        )

    def get(
        self,
        *,
        unit: PortfolioCategoryUnit,
        category: PortfolioCategory,
        percentage_base: PortfolioCategory = PortfolioCategory.TOTAL,
        percentage_unit: PortfolioCategoryUnit = PortfolioCategoryUnit.COUNT,
    ) -> Decimal:
        """Get the value of the portfolio in the given category and unit."""
        if unit == PortfolioCategoryUnit.PERCENTAGE:
            numerator = self.get(unit=percentage_unit, category=category)
            if not (denominator := self.get(unit=percentage_unit, category=percentage_base)):
                return Decimal(0)
            return round(Decimal(numerator / denominator), 3)

        return getattr(self, category.value).get(unit)
