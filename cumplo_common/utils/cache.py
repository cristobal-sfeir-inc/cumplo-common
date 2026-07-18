"""TTL cache utility with selective invalidation."""

from logging import getLogger
from typing import Any

from cachetools import TTLCache

logger = getLogger(__name__)


class Cache(TTLCache):
    """A custom TTL cache class."""

    def remove(self, **kwargs: Any) -> None:
        """Remove cache for a specific arguments and its values."""
        for key in self:
            if any(set(argument) <= set(key) for argument in kwargs.items()):
                logger.debug(f"Removing cache for {key=}")
                self.pop(key, None)  # noqa: B909
