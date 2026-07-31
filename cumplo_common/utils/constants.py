"""Environment-sourced constants used across the library."""

import json
import os

from dotenv import load_dotenv

load_dotenv()

# Basics
LOCATION = os.getenv("LOCATION", "us-central1")
PROJECT_ID = os.getenv("PROJECT_ID", "")
LOG_FORMAT = "\n%(levelname)s: %(message)s"
IS_TESTING = bool(os.getenv("IS_TESTING"))
SERVICE_ACCOUNT_EMAIL: str = os.getenv("SERVICE_ACCOUNT_EMAIL", "")

# Firestore Collections
KEYS_COLLECTION: str = os.getenv("KEYS_COLLECTION", "keys")
USERS_COLLECTION: str = os.getenv("USERS_COLLECTION", "users")
EMAILS_COLLECTION: str = os.getenv("EMAILS_COLLECTION", "emails")
DISABLED_COLLECTION: str = os.getenv("DISABLED_COLLECTION", "disabled")
# Cumplo
CUMPLO_BASE_URL: str = os.getenv("CUMPLO_BASE_URL", "")
SIMULATION_AMOUNT = int(os.getenv("SIMULATION_AMOUNT", "1000000"))

# Defaults
DEFAULT_EXPIRATION_MINUTES: int = int(os.getenv("DEFAULT_EXPIRATION_MINUTES", "60"))
SESSION_EXPIRATION_MINUTES: int = int(os.getenv("SESSION_EXPIRATION_MINUTES", "29"))
BALANCE_EXPIRATION_MINUTES: int = int(os.getenv("BALANCE_EXPIRATION_MINUTES", "3"))
INVESTMENT_EXPIRATION_MINUTES: int = int(os.getenv("INVESTMENT_EXPIRATION_MINUTES", "3"))

# Validators
PHONE_NUMBER_REGEX = r"^\+[1-9]\d{1,14}$"

# Cache
CACHE_MAXSIZE = int(os.getenv("CACHE_MAXSIZE", "1000"))
USERS_CACHE_TTL = int(os.getenv("USERS_CACHE_TTL", "600"))

# Encryption
PASSWORDS_ENCRYPTION_KEY: str = os.getenv("PASSWORDS_ENCRYPTION_KEY", "")

# Gmail
GMAIL_CREDENTIALS: dict[str, str] = json.loads(os.getenv("GMAIL_CREDENTIALS", "{}"))
GMAIL_FROM_EMAIL: str = os.getenv("GMAIL_FROM_EMAIL", "")
GMAIL_USER_ID: str = os.getenv("GMAIL_USER_ID", "me")
GMAIL_LABEL: str = os.getenv("GMAIL_LABEL", "")
GMAIL_TOPIC: str = os.getenv("GMAIL_TOPIC", "")
