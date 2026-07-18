"""Debtor domain model."""

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from .base_model import BaseModel
from .portfolio import Portfolio


class Debtor(BaseModel):
    """Debtor profile for a funding request."""

    share: Decimal = Field(...)
    name: str | None = Field(None)
    economic_sector: str | None = Field(None)
    portfolio: Portfolio = Field(...)
    description: str | None = Field(None)
    first_appearance: datetime = Field(...)
    dicom: bool | None = Field(None)
