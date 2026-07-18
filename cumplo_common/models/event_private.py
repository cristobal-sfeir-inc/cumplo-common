"""Internal (private) event definitions."""

from cumplo_common.models.funding_request import FundingRequest
from cumplo_common.models.investment import Investment
from cumplo_common.models.movement import Movement
from cumplo_common.models.user import User

from .utils import Event


class PrivateEvent(Event):
    """Events that can only be consumed internally."""

    # Events
    FUNDING_REQUEST_AVAILABLE = "funding_request.available", FundingRequest
    FUNDING_REQUEST_PROMISING = "funding_request.promising", FundingRequest, True

    USER_NOTIFICATIONS_UPDATED = "user.notifications.updated", User
    USER_CREDENTIALS_UPDATED = "user.credentials.updated", User
    USER_CHANNELS_UPDATED = "user.channels.updated", User
    USER_FILTERS_UPDATED = "user.filters.updated", User
    USER_DELETED = "user.deleted", User

    INVESTMENT_INITIALIZED = "investment.initialized", Investment
    INVESTMENT_SUBMITTED = "investment.submitted", Investment
    INVESTMENT_CONFIRMED = "investment.confirmed", Investment
    INVESTMENT_FAILED = "investment.failed", Investment
    INVESTMENT_REPAID = "investment.repaid", Investment
    INVESTMENT_REFUNDED = "investment.refunded", Investment
    INVESTMENT_DELINQUENT = "investment.delinquent", Investment
    INVESTMENT_CREDITED = "investment.credited", Investment
    INVESTMENT_UPDATED = "investment.updated", Investment

    # REVIEW: Maybe we don't event need withdrawal and deposit events. Could be just defined by the sign of the amount.
    MOVEMENT_WITHDRAWAL = "movement.withdrawal", Movement
    MOVEMENT_DEPOSIT = "movement.deposit", Movement

    # REVIEW: Should we use different events for this? Maybe this could be an Enum specifying the type.
    MOVEMENT_INVESTMENT = "movement.investment", Movement
    MOVEMENT_FEE_RETENTION = "movement.fee_retention", Movement
    MOVEMENT_FEE_CHARGE = "movement.fee_charge", Movement
    MOVEMENT_FEE_REFUND = "movement.fee_refund", Movement
    MOVEMENT_RETURN = "movement.return", Movement

    # Commands
    FUNDING_REQUEST_FILTER = "funding_request.filter", FundingRequest
