"""Main entry point for the FastAPI application."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from config_loader import load_toml_config, load_yaml_config
from core import validate_and_process
from logging_client import log_error, log_info

# ✅ Load and validate configurations
try:
    app_config = load_yaml_config()
    system_config = load_toml_config()
except ValueError as e:
    error_message = f"Configuration Error: {e}"
    raise SystemExit(error_message) from e

# ✅ Extract configurations
REQUIRED_PHRASES = app_config.required_phrases.model_dump()
PROHIBITED_PHRASES = set(app_config.prohibited_phrases)

PORT = system_config.server.port_no
WORKERS = system_config.server.number_of_workers
TIMEOUT = system_config.server.timeout_keep_alive

app = FastAPI(title="Customer Service AI")

ALLOWED_EXTENSIONS = {".wav", ".mp3"}  # Add allowed extensions here

@app.post("/process-audio/")
async def process_audio(
    audio_file: Annotated[UploadFile | None, File()] = None,
) -> JSONResponse:
    """Handle audio file upload and processing."""
    if audio_file is None:
        return JSONResponse(content={"error": "No file uploaded"}, status_code=400)
    file_extension = Path(audio_file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        allowed_formats = ", ".join(ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=400,
            detail=f"File format not supported. Allowed formats: {allowed_formats}",
        )

    temp_dir = Path("temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_audio_path = temp_dir / audio_file.filename

    try:
        with temp_audio_path.open("wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        log_info(f"Received file: {audio_file.filename}")
        log_info(f"Required Phrases: {REQUIRED_PHRASES}")
        log_info(f"Prohibited Phrases: {PROHIBITED_PHRASES}")

        # ✅ Process using core function with validated configurations
        result = validate_and_process(temp_audio_path, REQUIRED_PHRASES,
                                      PROHIBITED_PHRASES)

        if not result:
            return JSONResponse(
                content={"error": "Processing returned empty response"},
                status_code=500,
            )  # ✅ E501 Fix - Line wrapped
        return JSONResponse(content=result)

    except HTTPException as e:
        log_error(f"HTTP error: {e.detail}")
        return {"error": f"HTTP error: {e.detail}"}
    except OSError as e:
        log_error(f"File handling error: {e}")
        return {"error": "File handling error", "message": str(e)}
    except ValueError as e:
        log_error(f"Value error during processing: {e}")
        return {"error": "Value error during processing", "message": str(e)}

    finally:
        temp_audio_path.unlink(missing_ok=True)
        log_info(f"Deleted temp file: {temp_audio_path}")
