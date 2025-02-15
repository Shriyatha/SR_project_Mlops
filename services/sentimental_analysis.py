"""Module for call categorization based on transcript keywords."""

from __future__ import annotations

from textblob import TextBlob

"""
Module for performing sentiment analysis on text using TextBlob.
"""


def analyze_sentiment(text: str) -> dict[str, float | str]:
    """Analyze sentiment of a given text using TextBlob.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict[str, Union[float, str]]: Sentiment results

    """
    blob = TextBlob(text)
    polarity: float = blob.sentiment.polarity  # Range: [-1, 1]
    subjectivity: float = blob.sentiment.subjectivity  # Range: [0, 1]

    # Determine sentiment label
    if polarity > 0:
        sentiment_label = "positive"
    elif polarity < 0:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"

    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "sentiment": sentiment_label,
    }
