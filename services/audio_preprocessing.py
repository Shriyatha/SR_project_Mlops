"""Module for processing audio files.

This module handles transcription, compliance checking,
sentiment analysis, and speaker diarization.
"""

from collections.abc import Sequence
from pathlib import Path

from loguru import logger
from pydub import AudioSegment

from services.basic_categorization import categorize_call
from services.compliance import check_compliance
from services.pii_check import check_pii, mask_pii
from services.profanity_check import check_profanity, mask_profanity
from services.sentimental_analysis import analyze_sentiment
from services.speaking_speed import calculate_wpm
from services.speech_diarization import analyze_speaker_diarization
from services.transcription import transcribe_audio
from services.utils import clean_text


def validate_audio_file(audio_file: str, supported_formats: Sequence[str]) -> bool:
    """Validate the audio file to ensure it exists and is in a supported format."""
    file_path = Path(audio_file)
    if not file_path.is_file():
        logger.error(f"File does not exist: {audio_file}")
        return False

    if not any(file_path.suffix.lower() == f".{ext}" for ext in supported_formats):
        logger.error(
            f"Unsupported format for file: {audio_file}. "
            f"Supported: {', '.join(supported_formats)}",
        )
        return False

    logger.info(f"File validation successful: {audio_file}")
    return True


def get_audio_duration(file_path: str) -> float:
    """Get the duration of an audio file in seconds."""
    audio = AudioSegment.from_file(file_path)
    duration_seconds = len(audio) / 1000  # Convert milliseconds to seconds
    return round(duration_seconds, 2)


def process_audio_file(audio_file: str) -> dict:
    """Process an audio file to transcribe, clean, and analyze the transcript.

    Args:
        audio_file (str): Path to the audio file.

    Returns:
        dict: A dictionary containing all analysis results.

    """
    try:
        logger.info("Step 1: Transcribing Audio...")
        transcription = transcribe_audio(audio_file)

        if not transcription:
            logger.warning(f"Transcription failed for file: {audio_file}.")
            return {"error": "Transcription failed"}

        logger.info("Cleaning Transcript...")
        cleaned_transcript = clean_text(transcription)
        logger.info(f"Cleaned Transcript: {cleaned_transcript[:100]}..")

        logger.info("Step 2: Checking Compliance...")
        compliance_issues = check_compliance(cleaned_transcript)

        logger.info("Step 3: Checking for prohibited phrases...")
        cleaned_transcript = check_profanity(cleaned_transcript)

        logger.info("Step 4: Checking for PII...")
        detected_pii = check_pii(cleaned_transcript)

        cleaned_transcript = mask_profanity(cleaned_transcript)
        cleaned_transcript = mask_pii(cleaned_transcript)

        logger.info("Step 5: Performing Sentiment Analysis...")
        sentiment_result = analyze_sentiment(cleaned_transcript)

        logger.info("Step 6: Speaking Speed Analysis...")
        audio_duration = get_audio_duration(audio_file)
        wpm, evaluation = calculate_wpm(cleaned_transcript, audio_duration)

        logger.info("Step 7: Basic Categorization")
        call_category = categorize_call(cleaned_transcript)

        logger.info("Step 8: Speaker Diarization")
        diarization_results = analyze_speaker_diarization(audio_file)

        if diarization_results is not None:
            return {
                "transcription": cleaned_transcript,
                "compliance_issues": compliance_issues,
                "detected_pii": detected_pii,
                "sentiment": sentiment_result,
                "speaking_speed": {"wpm": wpm, "evaluation": evaluation},
                "call_category": call_category,
                "diarization_results": diarization_results,
            }
    except (OSError, ValueError) as e:
        logger.exception(f"Error processing {audio_file}: {e}")
        return {}
    return {...}
