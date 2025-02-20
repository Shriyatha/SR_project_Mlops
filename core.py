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
    "ignore",
    category=UserWarning,
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
    except CouldntDecodeError as e:
        logger.error(f"Invalid audio content: {e}")
        return False
    except ValueError as e:  # Catch only expected exceptions
        logger.error(f"Value error while processing audio: {e}")
        return False
    except OSError as e:  # Example: Handle file-related errors
        logger.error(f"OS error during audio processing: {e}")
        return False
    else:
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


def process_audio_file(
        audio_file: str,
        required_phrases: dict,
        prohibited_phrases: set,
    ) -> dict:
    """Process the audio file and extract necessary information."""
    try:
        cleaned_transcript = _transcribe_and_clean(audio_file)
        if not cleaned_transcript:
            return {"error": "Transcription failed"}
        msg = f"Cleaned Transcript (First 100 chars): {cleaned_transcript[:100]}..."
        logger.info(msg)

        # Compliance Check
        logger.info("Step 2: Checking Compliance...")
        compliance_issues = check_compliance(cleaned_transcript, required_phrases)
        if compliance_issues:
            logger.warning(f"Compliance Issues Found: {compliance_issues}")
        else:
            logger.info("All required compliance phrases are present.")
        logger.info("Compliance Check Completed.")

        # Prohibited Phrases Check
        logger.info("Step 3: Checking for prohibited phrases...")
        contains_prohibited = check_profanity(cleaned_transcript, prohibited_phrases)
        if contains_prohibited:
            logger.warning("Prohibited phrases detected. Masking now...")
            cleaned_transcript = mask_profanity(cleaned_transcript, prohibited_phrases)
        logger.info("Profanity Check Completed.")

        # PII Check
        logger.info("Step 4: Checking for PII...")
        detected_pii = check_pii(cleaned_transcript)
        cleaned_transcript = mask_pii(cleaned_transcript)
        logger.info(f"Detected PII: {detected_pii}")
        logger.info("PII Check Completed.")

        # Extract timestamps for found phrases
        logger.info("Step 5: Extracting timestamps for detected phrases...")
        found_phrases = extract_timestamps(cleaned_transcript, required_phrases)
        for category, phrases in found_phrases.items():
            for phrase, start, end in phrases:
                logger.info(f"{category.capitalize()}: '{phrase}' at [{start}, {end}]")
        logger.info("Timestamps extraction completed.")

        # Sentiment Analysis
        logger.info("Step 6: Performing Sentiment Analysis...")
        sentiment_result = analyze_sentiment(cleaned_transcript)
        logger.info(f"Sentiment Analysis Result: {sentiment_result}")

        # Speaking Speed Analysis
        logger.info("Step 7: Speaking Speed Analysis...")
        audio_duration = get_audio_duration(audio_file)
        wpm, evaluation = calculate_wpm(cleaned_transcript, audio_duration)
        logger.info(f"Speaking Speed: {wpm} WPM ({evaluation})")

        # Categorization
        logger.info("Step 8: Categorizing Call...")
        call_category = categorize_call(cleaned_transcript)
        logger.info(f"Call Category: {call_category}")

        # Speaker Diarization
        logger.info("Step 9: Performing Speaker Diarization...")
        diarization_results = analyze_speaker_diarization(audio_file)
        logger.info(
            f"Customer-to-Agent Speaking Ratio: "
            f"{diarization_results['speaking_ratio']}",
        )
        logger.info(f"Agent Interruptions: {diarization_results['interruptions']}")
        logger.info(f"Average TTFT: {diarization_results['ttft']} seconds")

        # Return final analysis results
        result = {
            "transcription": cleaned_transcript,
            "compliance_issues": compliance_issues,
            "contains_prohibited": contains_prohibited,
            "sentiment": sentiment_result,
            "speaking_speed": {"wpm": wpm, "evaluation": evaluation},
            "call_category": call_category,
            "diarization": diarization_results,
            "cleaned_transcript": cleaned_transcript,
        }

        if result:
            logger.info("Processing completed successfully.")
            return result
        logger.warning("Processing did not return a valid result.")

    except FileNotFoundError:
        logger.error(f"File not found: {audio_file}")
        return {"error": "File not found"}

def validate_and_process(
        audio_file: str,
        required_phrases: dict,
        prohibited_phrases: set,
    ) -> dict:
    """Validate the audio file and process it."""
    logger.info(f"Initializing process for file: {audio_file}")

    # Supported audio formats
    supported_formats = [".wav", ".mp3"]

    # Validate the audio file
    if not validate_audio_file(audio_file, supported_formats):
        logger.error(f"Validation failed for file: {audio_file}")
        return {"error": "Invalid audio format"}

    # Process the audio file
    logger.info(f"Processing file: {audio_file}")
    return process_audio_file(audio_file, required_phrases, prohibited_phrases)