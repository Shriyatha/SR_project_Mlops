"""Module for detecting and masking profanity in text."""

import re
from collections.abc import Sequence


def check_profanity(text: str, prohibited_phrases: Sequence[str]) -> bool:
    """Check for the presence of profane words in the text.

    Args:
        text (str): The input text to check.
        prohibited_phrases (Sequence[str]): A list of prohibited words/phrases.

    Returns:
        bool: True if profanity is detected, otherwise False.

    """
    words = re.findall(r"\b\w+\b", text.lower())  # Extract words, ignoring punctuation
    return any(word in prohibited_phrases for word in words)


def mask_profanity(text: str, prohibited_phrases: Sequence[str]) -> str:
    """Mask profane words in the text by replacing them with asterisks (*).

    Preserves punctuation.

    Args:
        text (str): The input text to process.
        prohibited_phrases (Sequence[str]): A list of prohibited words/phrases.

    Returns:
        str: The text with profane words masked.

    """

    def mask_word(match: re.Match[str]) -> str:
        """Replace profane words with asterisks."""
        word = match.group(0)
        return "*" * len(word) if word.lower() in prohibited_phrases else word

    return re.sub(r"\b\w+\b", mask_word, text)
