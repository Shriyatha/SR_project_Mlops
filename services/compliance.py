"""Module for compliance checking and timestamp extraction in transcripts."""
from __future__ import annotations

import logging

import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
logger = logging.getLogger(__name__)

def check_compliance(
    transcript: str, required_phrases: dict[str, list[str]],
) -> dict[str, bool]:
    """Check if all required categories are present in the transcript."""
    transcript = transcript.lower()
    compliance_issues = {}

    logger.info("Starting compliance check...")
    for category, phrases in required_phrases.items():
        found = any(phrase.lower() in transcript for phrase in phrases)
        compliance_issues[category] = found  # True if category is compliant
        logger.debug("Category: %s, Found: %s", category, found)

    logger.info("Compliance check completed: %s", compliance_issues)
    return compliance_issues


def extract_timestamps(
    transcript: str,
    required_phrases: dict[str, list[str]],
    compliant_categories: dict[str, bool],
) -> dict[str, list[tuple[str, int, int]]]:
    """Extract timestamps of required phrases in the transcript."""
    found_phrases: dict[str, list[tuple[str, int, int]]] = {}

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for category, phrases in required_phrases.items():
        if compliant_categories.get(category):  # Only process compliant categories
            patterns = [nlp(phrase) for phrase in phrases]
            matcher.add(category, patterns)

    doc = nlp(transcript)
    matches = matcher(doc)
    for match_id, start, end in matches:
        category = nlp.vocab.strings[match_id]
        phrase = doc[start:end].text
        if category not in found_phrases:
            found_phrases[category] = []
        found_phrases[category].append((phrase, start, end))

    return found_phrases


def analyze_transcript(
    transcript: str, required_phrases: dict[str, list[str]],
) -> dict[str, dict]:
    """Analyze compliance and return timestamps only for found compliances."""
    compliance_issues = check_compliance(transcript, required_phrases)

    # Extract timestamps only for compliant phrases
    found_phrases = extract_timestamps(transcript, required_phrases, compliance_issues)

    return {
        "compliance_issues": compliance_issues,
        "found_phrases": found_phrases,
    }
