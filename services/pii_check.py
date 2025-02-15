"""Module for detecting and masking (PII) in text."""

import re

# Define refined PII patterns
PII_PATTERNS: dict[str, str] = {
    "PHONE_NUMBER": r"\+?\d{1,2}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "EMAIL": r"\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b",
    "CREDIT_CARD": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "PIN": r"\b(?!\d{2}[-/]\d{2}[-/])\d{4,6}\b",
    "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "DATE_OF_BIRTH": r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",
}

MASKING_RULES: dict[str, str] = {
    "PHONE_NUMBER": "****-****-****-****",
    "SSN": "***-**-****",
    "CREDIT_CARD": "****-****-****-****",
    "IP_ADDRESS": "***.***.***.***",
    "DATE_OF_BIRTH": "**/**/****",
}


def check_pii(text: str) -> list[str]:
    """Identify PII in the given text.

    Args:
        text (str): The input text to analyze.

    Returns:
        list[str]: Names of detected PII entities.

    """
    return [
        entity for entity, pattern in PII_PATTERNS.items() if re.search(pattern, text)
    ]


def mask_pii(text: str) -> str:
    """Mask PII in the text based on predefined patterns.

    Args:
        text (str): The input text containing potential PII.

    Returns:
        str: The masked text with PII replaced.

    """

    def replace_match(match: re.Match[str], entity: str) -> str:
        """Replace matched PII with masked values."""
        text_match = match.group(0)
        if entity in MASKING_RULES:
            return MASKING_RULES[entity]
        if entity == "EMAIL":
            return f"{match.group(1)[0]}****@{match.group(2)}"  # Keep first letter
        if entity == "PIN":
            return "*" * len(text_match)  # Fully mask PIN
        return text_match  # Default: return unchanged

    # Mask PII
    for entity, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, lambda m, e=entity: replace_match(m, e), text)

    return text
