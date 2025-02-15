"""Module for compliance checking and timestamp extraction in transcripts."""
from __future__ import annotations

from spacy.matcher import PhraseMatcher
import spacy

nlp = spacy.load("en_core_web_sm")


def check_compliance(
    transcript: str, required_phrases: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Check if all required categories are present in the transcript."""
    transcript = transcript.lower()
    missing_details = {
        category: phrases for category, phrases in required_phrases.items()
        if not any(phrase.lower() in transcript for phrase in phrases)
    }
    return missing_details


def extract_timestamps(
    transcript: str,
    required_phrases: dict[str, list[str]],
) -> dict[str, list[tuple[str, int, int]]]:
    """Extract timestamps of required phrases in the transcript."""
    found_phrases: dict[str, list[tuple[str, int, int]]] = {
        category: [] for category in required_phrases
    }

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for category, phrases in required_phrases.items():
        patterns = [nlp(phrase) for phrase in phrases]
        matcher.add(category, patterns)

    doc = nlp(transcript)
    matches = matcher(doc)
    for match_id, start, end in matches:
        category = nlp.vocab.strings[match_id]
        phrase = doc[start:end].text
        found_phrases[category].append((phrase, start, end))

    return found_phrases


def analyze_transcript(
    transcript: str, required_phrases: dict[str, list[str]],
) -> dict[str, dict]:
    """Analyze compliance and timestamps for the given transcript."""
    compliance_issues = check_compliance(transcript, required_phrases)
    found_phrases = extract_timestamps(transcript, required_phrases)

    return {
        "compliance_issues": compliance_issues,
        "found_phrases": found_phrases,
    }