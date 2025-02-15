import gradio as gr
import httpx

API_URL = "http://127.0.0.1:8000/process-audio/"

def gradio_interface(audio_file):
    """Calls FastAPI backend for processing the uploaded audio file with an increased timeout.
    """
    try:
        with open(audio_file, "rb") as file_data:
            files = {"audio_file": (audio_file, file_data, "audio/wav")}

            # Increase timeout to prevent request failures
            with httpx.Client(timeout=300.0) as client:  # 300 seconds (5 minutes)
                response = client.post(API_URL, files=files)

            print("Response Status Code:", response.status_code)
            print("Response Text:", response.text)

            if response.status_code == 200:
                return response.json()
            return {"error": f"Backend error: {response.text}"}

    except httpx.TimeoutException:
        return {"error": "Request timed out. Try again with a smaller file."}

    except Exception as e:
        return {"error": f"Exception: {e!s}"}

# Create Gradio interface
interface = gr.Interface(
    fn=gradio_interface,
    inputs=gr.Audio(type="filepath", label="Upload Audio File"),
    outputs="json",
    title="Audio Processing App",
    description="Upload an audio file (.wav or .mp3) to process it.",
)

if __name__ == "__main__":
    interface.launch() 