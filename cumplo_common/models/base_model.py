"""Abstract base model shared across all domain models."""

from abc import ABC
from json import loads
from typing import Any

import pydantic
from pydantic import ConfigDict
from ulid import ULID


class BaseModel(pydantic.BaseModel, ABC):
    """Base class for all models in the project."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        json_encoders={ULID: str},
        validate_assignment=True,
        validate_default=True,
    )

    def __hash__(self) -> int:
        """Return hash based on non-id field values."""
        return hash(self.model_dump_json(exclude={"id"}, exclude_none=True))

    def __str__(self) -> str:
        """Return JSON string representation."""
        return self.model_dump_json(exclude_none=True)

    def __repr__(self) -> str:
        """Return JSON string representation."""
        return self.model_dump_json(exclude_none=True)

    def __eq__(self, other: object) -> bool:
        """Return True if hashes match."""
        return self.__hash__() == other.__hash__()

    def json(self, *args: Any, **kwargs: Any) -> dict:  # type: ignore[override]
        """
        Return the model as a JSON parsed dict.

        Returns:
            dict:JSON parsed dict representation of the model

        """
        return loads(self.model_dump_json(*args, **kwargs, exclude_none=True))
