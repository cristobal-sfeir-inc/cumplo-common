"""FastAPI dependency for authenticating incoming requests."""

from http import HTTPStatus
from logging import getLogger
from typing import Annotated

from fastapi import Header
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from cumplo_common.database import firestore

logger = getLogger(__name__)


def authenticate(request: Request, x_api_key: Annotated[str | None, Header()] = None) -> None:
    """
    Authenticate a request using either the X-API-KEY header or the user's ID in the event attributes.

    Args:
        request (Request): The request to authenticate
        x_api_key (Annotated[str  |  None, Header], optional): API key header. Defaults to None.

    Raises:
        HTTPException: When the API key is not present or invalid

    """
    if x_api_key:
        try:
            user = firestore.client.users.get(api_key=x_api_key)
        except (KeyError, ValueError) as exception:
            logger.debug(f"Authentication error: {exception}")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED) from None

    elif event := getattr(request.state, "event", None):
        try:
            user = firestore.client.users.get(id_user=event.id_user)
        except (KeyError, ValueError):
            logger.debug("Received invalid user ID")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED) from None

    else:
        logger.debug("No authentication method provided")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    request.state.user = user
