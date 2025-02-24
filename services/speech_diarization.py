"""Speech Diarization Module."""

import os
from collections import defaultdict
from typing import Any

from dotenv import load_dotenv
from pyannote.audio.pipelines import SpeakerDiarization

# Load pretrained pipeline from Hugging Face
load_dotenv()

# Get Hugging Face token from environment
HF_TOKEN = os.getenv("HUGGINGFACE_AUTH_TOKEN")

if HF_TOKEN is None:
    error_msg = "HUGGINGFACE_AUTH_TOKEN is not set. Please check your .env file."
    raise ValueError(error_msg)

# Load pretrained pipeline from Hugging Face using the token
pipeline = SpeakerDiarization.from_pretrained(
    "pyannote/speaker-diarization-3.0",
    use_auth_token=HF_TOKEN,
)

MIN_SPEAKERS = 2  # Constant to replace magic number


def analyze_speaker_diarization(audio_file: str) -> dict[str, Any]:
    """Perform speaker diarization.

    Computes speaking ratio, interruptions, and TTFT.

    Args:
        audio_file (str): Path to the audio file.

    Returns:
        dict: A dictionary containing speaking ratio, interruptions, and TTFT.

    """
    # Run speaker diarization
    diarization = pipeline(audio_file)

    # Store speaker durations and turns
    speaker_durations = defaultdict(float)
    speaker_turns = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        duration = turn.end - turn.start
        speaker_durations[speaker] += duration
        speaker_turns.append((turn.start, turn.end, speaker))

    if len(speaker_durations) < MIN_SPEAKERS:
        return {"speaking_ratio": 1.0, "interruptions": 0, "ttft": 0.0}

    # Identify customer and agent
    customer_speaker = min(speaker_durations, key=speaker_durations.get)
    agent_speaker = max(speaker_durations, key=speaker_durations.get)

    # Calculate speaking ratio
    customer_time = speaker_durations[customer_speaker]
    agent_time = speaker_durations[agent_speaker]
    speaking_ratio = customer_time / (agent_time + 1e-6)

    # Count agent interruptions
    agent_interruptions = sum(
        1
        for i in range(1, len(speaker_turns))
        if (
            speaker_turns[i][2] == agent_speaker
            and speaker_turns[i - 1][2] == customer_speaker
            and speaker_turns[i][0] < speaker_turns[i - 1][1]
        )
    )


    # Compute TTFT (Time to First Token)
    ttft_values = [
        speaker_turns[i][0] - speaker_turns[i - 1][1]
        for i in range(1, len(speaker_turns))
        if (
            speaker_turns[i - 1][2] == customer_speaker
            and speaker_turns[i][2] == agent_speaker
        )
    ]

    avg_ttft = sum(ttft_values) / len(ttft_values) if ttft_values else 0.0


    return {
        "speaking_ratio": round(speaking_ratio, 2),
        "interruptions": agent_interruptions,
        "ttft": round(avg_ttft, 2),
    }
