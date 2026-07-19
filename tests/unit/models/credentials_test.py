import pytest
from cryptography.fernet import Fernet
from pydantic import ValidationError

from cumplo_common.models.credentials import Credentials
from cumplo_common.utils.constants import PASSWORDS_ENCRYPTION_KEY

PASSWORD = "mypassword123"  # noqa: S105


class TestCredentials:
    def test_credentials_initialization(self) -> None:
        """Test basic initialization of Credentials."""
        creds = Credentials(
            email="test@example.com",
            password=PASSWORD,
            user_id="12345",
            company_id="67890",
            company_nin="1234567890",
        )

        assert creds.email == "test@example.com"
        assert creds.user_id == "12345"
        # Password should be encrypted
        assert creds.password.startswith("gAAAAA")

    def test_password_encryption(self) -> None:
        """Test that password is properly encrypted."""
        original_password = PASSWORD
        creds = Credentials(
            email="test@example.com",
            password=original_password,
            user_id="12345",
            company_id="67890",
            company_nin="1234567890",
        )

        # Verify encryption happened
        assert creds.password != original_password
        assert creds.password.startswith("gAAAAA")

        # Verify we can decrypt it back
        cipher_suite = Fernet(PASSWORDS_ENCRYPTION_KEY)
        decrypted = cipher_suite.decrypt(creds.password.encode("utf-8")).decode("utf-8")
        assert decrypted == original_password

    def test_password_decryption(self) -> None:
        """Test the decrypted_password computed field."""
        original_password = PASSWORD
        creds = Credentials(
            email="test@example.com",
            password=original_password,
            user_id="12345",
            company_id="67890",
            company_nin="1234567890",
        )

        assert creds.decrypted_password == original_password

    def test_already_encrypted_password(self) -> None:
        """Test that an already encrypted password is not re-encrypted."""
        original_password = PASSWORD
        # First, create credentials to get an encrypted password
        creds1 = Credentials(
            email="test@example.com",
            password=original_password,
            user_id="12345",
            company_id="67890",
            company_nin="1234567890",
        )
        encrypted_password = creds1.password

        # Now create new credentials with the encrypted password
        creds2 = Credentials(
            email="test@example.com",
            password=encrypted_password,
            user_id="12345",
            company_id="67890",
            company_nin="1234567890",
        )

        # Password should remain the same
        assert creds2.password == encrypted_password
        assert creds2.decrypted_password == original_password

    def test_invalid_credentials(self) -> None:
        """Test that invalid credentials raise appropriate errors."""
        with pytest.raises(ValidationError, match="email"):
            Credentials(
                email="not_an_email",
                password=PASSWORD,
                user_id="12345",
                company_id="67890",
                company_nin="1234567890",
            )

        with pytest.raises(ValidationError, match="password"):
            Credentials(
                email="test@example.com",
                password="",
                user_id="12345",
                company_id="67890",
                company_nin="1234567890",
            )

    def test_valid_email_formats(self) -> None:
        """Test that various valid email formats are accepted."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.com",
            "user+tag@example.co.uk",
            "123@domain.com",
            "user-name@domain-test.com",
            "user_name@domain.io",
        ]
        for email in valid_emails:
            Credentials(
                email=email,
                password=PASSWORD,
                user_id="12345",
                company_id="67890",
                company_nin="1234567890",
            )

    def test_invalid_email_formats(self) -> None:
        """Test that invalid email formats raise validation errors."""
        invalid_emails = [
            "not_an_email",
            "@domain.com",
            "user@",
            "user@.com",
            "user@domain.",
            "user name@domain.com",
            "user@domain..com",
            "user@domain@domain.com",
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError, match="email"):
                Credentials(
                    email=email,
                    password=PASSWORD,
                    user_id="12345",
                    company_id="67890",
                    company_nin="1234567890",
                )
