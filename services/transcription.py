"""Module for transcribing audio using Whisper."""

from __future__ import annotations  # For better type annotations

import logging
import time
import warnings
from pathlib import Path

import whisper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Suppress specific warnings
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".torch.load.",
)
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=".FP16 is not supported on CPU.",
)


def transcribe_audio(audio_file: str | Path, retries: int = 3) -> str | None:
    """Transcribes an audio file using OpenAI's Whisper model.

    Args:
        audio_file (str | Path): Path to the audio file (as a string or Path object).
        retries (int, optional): Number of retry attempts in case of failure.
            Defaults to 3.

    Returns:
        str | None: Transcribed text if successful, otherwise None.

    """
    # Convert PosixPath to string if necessary
    if isinstance(audio_file, Path):
        audio_file = str(audio_file)

    # Check if the file exists
    if not Path(audio_file).exists():
        logger.error("❌ Audio file not found: %s", audio_file)
        return None

    # Load the Whisper model
    model = whisper.load_model("base")

    for attempt in range(1, retries + 1):
        logger.info("🎙️ Transcribing audio (Attempt %d/%d)...", attempt, retries)
        try:
            # Transcribe the audio file
            result = model.transcribe(audio_file)
            return result["text"]
        except Exception as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise  # Don't suppress system exit signals

            logger.exception("❌ Error during transcription")  # ✅ No need to pass 'e'

            if attempt < retries:
                logger.info("🔄 Retrying in 2 seconds...")
                time.sleep(2)
    logger.error("❌ Max retries reached. Could not transcribe the audio.")
    return None
