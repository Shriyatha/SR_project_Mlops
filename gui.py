"""GUI module for interacting with the FastAPI backend."""

from pathlib import Path

import gradio as gr
import httpx

API_URL = "http://127.0.0.1:8000/process-audio/"
status_code = 200
def gradio_interface(audio_file: str) -> dict:
    """Call FastAPI backend to process the uploaded audio file."""
    try:
        with Path.open(audio_file, "rb") as file_data:
            files = {"audio_file": (audio_file, file_data, "audio/wav")}

            # Increase timeout to prevent request failures
            with httpx.Client(timeout=300.0) as client:  # 300 seconds (5 minutes)
                response = client.post(API_URL, files=files)

            if response.status_code == status_code:
                return response.json()
            return {"error": f"Backend error: {response.text}"}

    except httpx.TimeoutException:
        return {"error": "Request timed out. Try again with a smaller file."}

    except FileNotFoundError:
        return {"error": "File not found. Please upload a valid audio file."}

    except IsADirectoryError:
        return {"error": "Expected a file but received a directory."}

    except ValueError as error:
        return {"error": f"Invalid input: {error!s}"}

# Create Gradio interface
interface = gr.Interface(
    fn=gradio_interface,
    inputs=gr.Audio(type="filepath", label="Upload Audio File"),
    outputs="json",
    title="Audio Processing App",
    description="Upload an audio file (.wav or .mp3) for processing.",
    live=True,  # Enables real-time updates
    allow_flagging="never",  # Disable unnecessary flagging
    examples=[["example_audio.wav"], ["example_audio.mp3"]],  # Provide sample files
    theme="soft",  # Improve UI aesthetics
)

if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860, debug=True)
