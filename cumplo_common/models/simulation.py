"""Simulation and installment models for funding-request projections."""

from datetime import datetime
from decimal import Decimal
from functools import cached_property

from pydantic import Field, computed_field

from cumplo_common.utils.constants import SIMULATION_AMOUNT

from .base_model import BaseModel


class SimulationInstallment(BaseModel):
    """Single installment in a funding-request simulation."""

    amount: int = Field(...)
    capital: int = Field(...)
    exit_fee: int = Field(...)
    interest: int = Field(...)
    date: datetime = Field(...)


class Simulation(BaseModel):
    """Simulation result for a funding request."""

    exit_fee: int = Field(...)
    upfront_fee: int = Field(...)
    net_returns: int = Field(...)
    capital: int = Field(SIMULATION_AMOUNT)
    installments: list[SimulationInstallment] = Field(default_factory=list)

    @computed_field  # type: ignore[misc]
    @cached_property
    def investment(self) -> int:
        """Returns the investment of the simulation."""
        return self.capital + self.upfront_fee

    @cached_property
    def profit_rate(self) -> Decimal:
        """Returns the profit rate of the simulation."""
        return round(Decimal((self.capital + self.net_returns) / self.investment - 1), 4)
