"""Module for calculating speaking speed in Words Per Minute (WPM)."""

from __future__ import annotations  # Ensure list[str] works in older Python versions

# Constants for speaking speed thresholds
SLOW_WPM_THRESHOLD = 125
OPTIMAL_WPM_THRESHOLD = 175


def calculate_wpm(transcript: str, call_duration_seconds: float) -> tuple[float, str]:
    """Calculate Words Per Minute (WPM) and evaluate speaking speed.

    Args:
        transcript (str): The transcribed speech.
        call_duration_seconds (float): The duration of the call in seconds.

    Returns:
        tuple[float, str]:
            - WPM (words per minute)
            - Speed evaluation ("Too Slow", "Optimal", "Too Fast")

    """
    word_count = len(transcript.split())
    wpm = round((word_count / call_duration_seconds) * 60, 2)

    # Define speaking speed evaluation
    if wpm < SLOW_WPM_THRESHOLD:
        speed_evaluation = "Too Slow 🐢"
    elif SLOW_WPM_THRESHOLD <= wpm <= OPTIMAL_WPM_THRESHOLD:
        speed_evaluation = "Optimal ✅"
    else:
        speed_evaluation = "Too Fast 🚀"

    return wpm, speed_evaluation
