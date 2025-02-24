"""Core module for processing customer service audio files."""

import json
import warnings
from pathlib import Path

from loguru import logger
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from services.audio_preprocessing import get_audio_duration
from services.basic_categorization import categorize_call
from services.compliance import check_compliance, extract_timestamps
from services.pii_check import check_pii, mask_pii
from services.profanity_check import check_profanity, mask_profanity
from services.sentimental_analysis import analyze_sentiment
from services.speaking_speed import calculate_wpm
from services.speech_diarization import analyze_speaker_diarization
from services.transcription import transcribe_audio
from services.utils import clean_text

# Suppress warnings
warnings.filterwarnings(
    "ignore", category=UserWarning, message=".*FP16 is not supported on CPU.*",
)
warnings.filterwarnings(
    "ignore", category=UserWarning,
    message="The MPEG_LAYER_III subtype is unknown to TorchAudio",
)
warnings.filterwarnings("ignore", category=FutureWarning, message=".*torch.load.*")

# Load logging configuration from config file
config_path = Path("config.json")
with config_path.open() as config_file:
    config = json.load(config_file)

# Configure loguru logger
logger.add(
    config["logging"]["log_file_name"],
    rotation=config["logging"]["log_rotation"],
    compression=config["logging"]["log_compression"],
    level=config["logging"]["min_log_level"],
)

def validate_audio_file(file_path: str, supported_formats: list) -> bool:
    """Validate the audio file format and content."""
    file_extension = Path(file_path).suffix.lower()
    if file_extension not in supported_formats:
        logger.error(f"Unsupported file extension: {file_extension}")
        return False
    try:
        audio = AudioSegment.from_file(file_path)
        logger.info(f"Audio file loaded successfully: {file_path}")
        logger.info(f"Audio duration: {len(audio)} ms")
    except (CouldntDecodeError, ValueError, OSError) as e:
        logger.error(f"Error processing audio: {e}")
        return False
    return True

def _transcribe_and_clean(audio_file: str) -> str:
    """Transcribe and clean the audio file."""
    logger.info("Step 1: Transcribing Audio...")
    transcription = transcribe_audio(audio_file)

    if not transcription:
        logger.warning(f"Transcription failed for file: {audio_file}.")
        return ""

    logger.info("Cleaning Transcript...")
    return clean_text(transcription)

def sentimental_ana(cleaned_transcript: str) -> dict:
    """Perform sentiment analysis on the cleaned transcript."""
    logger.info("Performing sentiment analysis...")
    return analyze_sentiment(cleaned_transcript)

def call_category(cleaned_transcript: str) -> list:
    """Categorize the call based on the cleaned transcript."""
    logger.info("Categorizing the call...")
    return categorize_call(cleaned_transcript)

def process_audio_file(audio_file: str,
        required_phrases: dict, prohibited_phrases: set) -> dict:
    """Process the audio file and extract all possible information."""
    try:
        logger.info(f"Processing started for file: {audio_file}")

        # Transcription & Cleaning
        logger.info("Starting transcription and cleaning process...")
        cleaned_transcript = _transcribe_and_clean(audio_file)
        if not cleaned_transcript:
            logger.error("Transcription failed.")
            return {"error": "Transcription failed"}
        logger.info("Transcription completed.")

        logger.info("Performing compliance check...")
        compliance_issues = check_compliance(cleaned_transcript, required_phrases)
        compliant_categories = {k: v for k, v in compliance_issues.items() if v}
        if compliance_issues:
            logger.warning(f"Compliance issues found: {compliance_issues}")

        logger.info("Checking for prohibited phrases...")
        contains_prohibited = check_profanity(cleaned_transcript, prohibited_phrases)
        if contains_prohibited:
            logger.warning("Prohibited phrases detected.")
            masked_transcript = mask_profanity(cleaned_transcript, prohibited_phrases)
            logger.info("Prohibited phrases masked.")
        else:
            masked_transcript = cleaned_transcript
            logger.info("No prohibited phrases detected.")

        # PII Check
        logger.info("Checking for PII...")
        detected_pii = check_pii(cleaned_transcript)
        if detected_pii:
            logger.warning(f"Detected PII: {detected_pii}")
        masked_transcript = mask_pii(masked_transcript)
        logger.info("PII masked if found.")

        # Extract timestamps (ONLY for compliant categories)
        logger.info("Extracting timestamps for found compliant phrases...")
        found_phrases = extract_timestamps(cleaned_transcript,
                            required_phrases, compliant_categories)
        if found_phrases:
            logger.info(f"Timestamps extracted: {found_phrases}")
        else:
            logger.info("No timestamps found for compliant phrases.")

        # Sentiment Analysis
        sentiment_result = sentimental_ana(cleaned_transcript)
        logger.info(f"Sentiment Analysis Result: {sentiment_result}")

        # Speaking Speed Analysis
        logger.info("Calculating speaking speed...")
        audio_duration = get_audio_duration(audio_file)
        wpm, evaluation = calculate_wpm(cleaned_transcript, audio_duration)
        logger.info(f"Speaking Speed: {wpm} WPM ({evaluation})")

        # Categorization
        call_category11 = call_category(cleaned_transcript)
        logger.info(f"Call categorized as: {call_category11}")

        # Speaker Diarization
        logger.info("Performing speaker diarization...")
        diarization_results = analyze_speaker_diarization(audio_file)
        logger.info(f"Diarization results: {diarization_results}")

        # Compile results
        result = {
            "transcription": cleaned_transcript,
            "masked_transcription": masked_transcript,
            "compliance_issues": compliance_issues,
            "contains_prohibited": contains_prohibited,
            "detected_pii": detected_pii,
            "timestamps": found_phrases,
            "sentiment": sentiment_result,
            "speaking_speed": {"wpm": wpm, "evaluation": evaluation},
            "call_category": call_category11,
            "diarization": diarization_results,
            "audio_duration_ms": audio_duration,
        }
        logger.info("Processing completed successfully.")

    except FileNotFoundError:
        logger.error(f"File not found: {audio_file}")
        return {"error": "File not found"}
    else:
        return result

def validate_and_process(audio_file: str,
        required_phrases: dict, prohibited_phrases: set) -> dict:
    """Validate the audio file and process it."""
    logger.info(f"[START] Processing audio file: {audio_file}")

    supported_formats = [".wav", ".mp3"]
    if not validate_audio_file(audio_file, supported_formats):
        logger.error("[ERROR] Invalid audio format. Aborting processing.")
        return {"error": "Invalid audio format"}

    logger.info("[STEP 1] Valid Audio File Confirmed. Proceeding with transcription...")
    result = process_audio_file(audio_file, required_phrases, prohibited_phrases)

    if "error" in result:
        logger.error(f"[FAILURE] Processing failed: {result['error']}")
    else:
        logger.info(f"[SUCCESS] Processing completed successfully for {audio_file}")

    return result

