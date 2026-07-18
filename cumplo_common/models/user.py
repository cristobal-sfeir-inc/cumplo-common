"""User domain model with balance, portfolio, and session sub-models."""

# mypy: disable-error-code="misc, call-overload"

from datetime import UTC, datetime

import arrow
import ulid
from pydantic import Field, PositiveInt, field_validator

from cumplo_common.utils.constants import (
    BALANCE_EXPIRATION_MINUTES,
    DEFAULT_EXPIRATION_MINUTES,
    INVESTMENT_EXPIRATION_MINUTES,
)

from .base_model import BaseModel
from .channel import ChannelConfigurationType
from .credentials import Credentials
from .event_public import PublicEvent
from .filter_configuration import FilterConfiguration
from .investment import Investment
from .notification import Notification
from .session import Session
from .utils import EventModel


class Balance(BaseModel):
    """User cash balance with expiry tracking."""

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    amount: int = Field()

    @property
    def has_expired(self) -> bool:
        """Check if the balance has expired."""
        return arrow.get(self.updated_at).shift(minutes=BALANCE_EXPIRATION_MINUTES) < arrow.utcnow()


class InvestmentPortfolio(BaseModel):
    """Cached snapshot of a user's investments."""

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    investments: dict[int, Investment] = Field(default_factory=dict)

    @property
    def has_expired(self) -> bool:
        """Check if the investment portfolio has expired."""
        return arrow.get(self.updated_at).shift(minutes=INVESTMENT_EXPIRATION_MINUTES) < arrow.utcnow()


class User(BaseModel):
    """Cumplo platform user with preferences, credentials, and portfolio."""

    id: ulid.ULID = Field(...)
    api_key: str = Field(...)
    email: str = Field(...)
    is_admin: bool = Field(default=False)
    name: str = Field(..., max_length=30)
    credentials: Credentials | None = Field(None)
    expiration_minutes: PositiveInt = Field(DEFAULT_EXPIRATION_MINUTES)

    notifications: dict[str, Notification] = Field(default_factory=dict)
    filters: dict[str, FilterConfiguration] = Field(default_factory=dict)
    channels: dict[str, ChannelConfigurationType] = Field(default_factory=dict)

    balance: Balance | None = Field(None)
    portfolio: InvestmentPortfolio | None = Field(None)
    session: Session | None = Field(None)

    @field_validator("id", mode="before")
    @classmethod
    def _format_id(cls, value: str) -> ulid.ULID:
        """Format the ID field as an ULID object."""
        return value if isinstance(value, ulid.ULID) else ulid.parse(value)

    def should_notify(self, event: PublicEvent, content: EventModel) -> bool:
        """
        Check if the given user should be notified with the given event and content.

        Args:
            user (User): The user who's being notified
            event (Event): The event used to notify the user
            content (SubjectContent): The content of the notification

        Returns:
            bool: Whether the user has already been notified with the given event and content

        """
        if not event.is_recurring:
            return True

        id_notification = Notification.build_id(event, content.id)
        if not (notification := self.notifications.get(id_notification)):
            return True

        return notification.has_expired and not notification.dismissed
