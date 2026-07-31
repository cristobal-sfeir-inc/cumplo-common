"""Public event definitions."""

from cumplo_common.models.funding_request import FundingRequest

from .utils import Event


class PublicEvent(Event):
    """Events that can be publicly consumed."""

    FUNDING_REQUEST_PROMISING = "funding_request.promising", FundingRequest, True
