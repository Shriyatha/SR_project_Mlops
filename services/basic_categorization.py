"""Module for call categorization based on transcript keywords."""
import re


def categorize_call(transcript: str) -> list[str]:
    """Categorizes a call transcript into predefined categories.

    Uses keyword matching to classify the transcript.
    """
    categories: dict[str, list[str]] = {
        "Billing Issue": ["bill", "charge", "payment", "refund", "overcharged"],
        "Order Return": ["return", "exchange", "replace", "wrong item"],
        "Technical Support": ["error", "not working", "issue", "troubleshoot", "fix"],
        "Account Support": ["login", "password", "account locked", "reset"],
        "General Inquiry": ["information", "details", "help", "assist"],
    }

    if not transcript.strip():
        return ["Uncategorized"]

    detected_categories: set[str] = set()
    for category, keywords in categories.items():
        if any(
            re.search(rf"\b{re.escape(kw)}\b", transcript, re.IGNORECASE)
            for kw in keywords
        ):
            detected_categories.add(category)

    return sorted(detected_categories) if detected_categories else ["Uncategorized"]
