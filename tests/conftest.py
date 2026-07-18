import os

import pytest

# A valid 32-byte URL-safe base64 Fernet key for use in unit tests.
# Must be set before cumplo_common.utils.constants is imported so the module-level
# assignment picks it up.  Conftest runs before test modules are collected.
_TEST_FERNET_KEY = "nrHO2BCnj_wektC3Rd90qM5LzXHYcxwwWoNdwzqXf0M="
os.environ.setdefault("PASSWORDS_ENCRYPTION_KEY", _TEST_FERNET_KEY)


@pytest.fixture(autouse=True)
def patch_encryption_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the encryption key constant for every test that needs it."""
    monkeypatch.setattr("cumplo_common.models.credentials.PASSWORDS_ENCRYPTION_KEY", _TEST_FERNET_KEY)
    monkeypatch.setattr("cumplo_common.utils.constants.PASSWORDS_ENCRYPTION_KEY", _TEST_FERNET_KEY)
