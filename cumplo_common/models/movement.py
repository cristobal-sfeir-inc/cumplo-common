"""Movement domain model."""

from pydantic import BaseModel


class Movement(BaseModel):
    """Account movement (deposit, withdrawal, or fee)."""
