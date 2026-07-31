"""Filter configuration models for funding-request filtering."""

from decimal import Decimal
from json import loads
from typing import Any, Self

import ulid
from pydantic import Field, PositiveInt, field_validator, model_validator

from .base_model import BaseModel
from .credit import CreditType
from .portfolio import PortfolioCategory, PortfolioCategoryUnit


class PortfolioFilterConfiguration(BaseModel):
    """Filter configuration for a specific portfolio status and data unit."""

    unit: PortfolioCategoryUnit = Field(...)
    category: PortfolioCategory = Field(...)
    minimum: Decimal | None = Field(None, ge=0)
    maximum: Decimal | None = Field(None, ge=0)
    percentage_base: PortfolioCategory = Field(PortfolioCategory.TOTAL)
    percentage_unit: PortfolioCategoryUnit = Field(PortfolioCategoryUnit.AMOUNT)

    @model_validator(mode="after")
    def _validate_bounds(self) -> Self:
        """Validate that minimum and maximum values are within valid bounds."""
        if self.unit == PortfolioCategoryUnit.PERCENTAGE:
            if self.minimum is not None and self.minimum > 1:
                raise ValueError("Minimum percentage must be less than or equal to 1")
            if self.maximum is not None and self.maximum > 1:
                raise ValueError("Maximum percentage must be less than or equal to 1")

        if self.minimum is not None and self.maximum is not None and self.maximum <= self.minimum:
            raise ValueError("Maximum value must be greater than minimum value")

        return self


class FilterConfiguration(BaseModel):
    """Configuration settings for filtering funding requests."""

    id: ulid.ULID = Field(...)
    name: str | None = Field(None)
    minimum_amount: PositiveInt | None = Field(None)
    minimum_score: Decimal | None = Field(None, ge=0, le=1)
    target_credit_types: list[CreditType] | None = Field(None)

    minimum_duration: PositiveInt | None = Field(None)
    maximum_duration: PositiveInt | None = Field(None)
    minimum_investment_amount: PositiveInt | None = Field(None)

    minimum_irr: Decimal | None = Field(None, ge=0)
    minimum_monthly_profit_rate: Decimal | None = Field(None, ge=0)

    ignore_dicom: bool = Field(default=False)
    maximum_debtors: PositiveInt | None = Field(None)
    portfolio: list[PortfolioFilterConfiguration] = Field(default_factory=list)

    @field_validator("id", mode="before")
    @classmethod
    def _format_id(cls, value: ulid.default.api.ULIDPrimitive) -> ulid.ULID:
        """Format the ID field as an ULID object."""
        return ulid.parse(value)

    def __hash__(self) -> int:
        """Return the hash of the object."""
        return hash(self.model_dump_json(exclude={"id", "name"}, exclude_none=True))

    def json(self, *args: Any, **kwargs: Any) -> dict:  # type: ignore[override]
        """
        Return the model as a JSON parsed dict.

        Returns:
            dict: JSON parsed dict representation of the model

        """
        return loads(self.model_dump_json(*args, **kwargs, exclude_defaults=True))
