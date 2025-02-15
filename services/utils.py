"""Utility functions for text processing."""

import re
import unicodedata
from typing import AnyStr


def clean_text(text: AnyStr) -> str:
    """Clean and standardize input text.

    This function:
    - Normalizes Unicode characters (NFKD).
    - Removes non-ASCII characters.
    - Retains only alphanumeric characters and basic punctuation.
    - Replaces multiple spaces with a single space.
    - Converts text to lowercase.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned and standardized text.

    """
    if not isinstance(text, str):
        error_message = "Expected a string input."
        raise TypeError(error_message)

    # Normalize Unicode (NFKD) and remove non-ASCII characters
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)

    # Remove non-alphanumeric characters except spaces and basic punctuation
    text = re.sub(r"[^\w\s.,!?;]", "", text)

    # Normalize whitespace (remove extra spaces and trim)
    text = re.sub(r"\s+", " ", text).strip()

    # Convert to lowercase for standardization
    return text.lower()
