"""Session domain model."""

from datetime import datetime

import arrow
from pydantic import Field

from cumplo_common.utils.constants import SESSION_EXPIRATION_MINUTES

from .base_model import BaseModel


class Session(BaseModel):
    """Authenticated session token with expiry."""

    token: str = Field(...)
    date: datetime = Field(default_factory=lambda: arrow.utcnow().datetime)

    @property
    def has_expired(self) -> bool:
        """Check if the session has expired."""
        return arrow.get(self.date).shift(minutes=SESSION_EXPIRATION_MINUTES) < arrow.utcnow()

    @property
    def headers(self) -> dict[str, str]:
        """Get the headers for the session."""
        return {"authorization": f"Bearer {self.token}"}
