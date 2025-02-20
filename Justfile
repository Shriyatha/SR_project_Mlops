PYTHON := `command -v python3 || command -v python`

setup:
    uv venv .venv_test
    source .venv_test/bin/activate
    {{PYTHON}} -m ensurepip
    uv pip install --system -r requirements.txt
    {{PYTHON}} -m spacy download en_core_web_sm

run:
    bash -c "source .venv/bin/activate && \
    {{PYTHON}} logging_server.py & sleep 2 && \
    uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 & sleep 2 && \
    {{PYTHON}} gui.py && wait"
