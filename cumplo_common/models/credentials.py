"""User credentials model with encrypted password handling."""

import re
from typing import Any

from cryptography.fernet import Fernet
from pydantic import Field, field_validator

from cumplo_common.utils.constants import PASSWORDS_ENCRYPTION_KEY

from .base_model import BaseModel


class Credentials(BaseModel):
    """Cumplo user credentials with encrypted password storage."""

    email: str = Field(pattern=r"^[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,4}$")
    password: str = Field()
    user_id: str = Field(...)
    company_id: str = Field(...)
    company_nin: str = Field(...)
    valid: bool = Field(default=True)

    @property
    def decrypted_password(self) -> str:
        """Decrypt the password."""
        cipher_suite = Fernet(PASSWORDS_ENCRYPTION_KEY)
        decrypted_password = cipher_suite.decrypt(self.password.encode("utf-8"))
        return decrypted_password.decode("utf-8")

    @field_validator("password", mode="before")
    @classmethod
    def _password_setter(cls, value: Any) -> str:
        """Encrypt the password."""
        if not isinstance(value, str):
            raise TypeError("Password must be a string")

        if not value:
            raise ValueError("Password cannot be empty")

        # NOTE: Fernet tokens are base64-encoded and start with 'gAAAAA'
        if re.match(r"^gAAAAA", value):
            return value

        cipher_suite = Fernet(PASSWORDS_ENCRYPTION_KEY)
        encrypted_password = cipher_suite.encrypt(value.encode("utf-8"))
        return encrypted_password.decode("utf-8")
