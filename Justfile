# Set shell mode to work with environment variables
set shell := ["bash", "-c"]

# Load environment variables from .env file
set dotenv-load

PYTHON := `command -v python3 || command -v python`

setup:
    uv venv .venv_test
    source .venv_test/bin/activate
    {{PYTHON}} -m ensurepip --default-pip
    uv pip install --system -r requirements.txt
    {{PYTHON}} -m pip install --upgrade pip
    uv pip install git+https://github.com/openai/whisper.git
    {{PYTHON}} -m spacy download en_core_web_sm

run:
    source .venv_test/bin/activate
    {{PYTHON}} logging_server.py & sleep 2
    uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 & sleep 2
    {{PYTHON}} gui.py
    wait

docs:
    mkdocs serve
