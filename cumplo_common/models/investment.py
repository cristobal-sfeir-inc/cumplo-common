"""Investment domain model."""

from datetime import datetime

from pydantic import Field

from .base_model import BaseModel
from .credit import CreditType
from .funding_request import Duration


class Investment(BaseModel):
    """Single investment record on a funding request."""

    id: int = Field(...)
    id_funding_request: int = Field(...)
    credit_type: CreditType = Field(...)
    status: str = Field(...)
    currency: str = Field(...)

    borrower: str = Field(...)
    debtor: str = Field(...)

    amount: int = Field(...)
    exit_fee: int = Field(...)
    upfront_fee: int = Field(...)
    interest: int = Field(...)

    paid_capital: int = Field(...)
    insolvent_capital: int = Field(...)
    days_delinquent: int = Field(...)

    investment_date: datetime = Field(...)
    due_date: str = Field(...)
    duration: Duration = Field(...)
