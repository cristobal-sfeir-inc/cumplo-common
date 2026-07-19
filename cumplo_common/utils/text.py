"""Text cleaning and masking utilities."""

import string
import unicodedata

SEPARATORS = ["_", "-"]


def clean_text(error: str) -> str:
    """
    Clean a text by removing punctuation and normalizing unicode characters.

    Args:
        error (str): The text to be cleaned

    Returns:
        str: The cleaned text

    """
    for separator in SEPARATORS:
        error = " ".join(error.split(separator))

    return " ".join(
        unicodedata.normalize("NFD", error)
        .encode("ASCII", "ignore")
        .decode("UTF-8")
        .replace("\n", " ")
        .replace("\r", " ")
        .translate(str.maketrans("", "", string.punctuation))
        .upper()
        .split()
    )


def secure_key(key: str) -> str:
    """
    Return a secure version of a key for logging purposes.

    Args:
        key (str): The key to be secured

    Returns:
        str: A loggable version of the key

    """
    return f"{key[:5]}{'*' * (len(key) - 15)}{key[-10:]}"
