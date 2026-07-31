"""Borrower domain model."""

from datetime import datetime

from pydantic import Field

from .base_model import BaseModel
from .portfolio import Portfolio


class Borrower(BaseModel):
    """Borrower profile for a funding request."""

    id: int | None = Field(None)
    name: str | None = Field(None)
    economic_sector: str | None = Field(None)
    description: str | None = Field(None)
    first_appearance: datetime | None = Field(None)
    portfolio: Portfolio = Field(...)
    dicom: bool | None = Field(None)
