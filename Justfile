# ✅ Install dependencies using uv
setup:
    uv venv .venv
    source .venv/bin/activate
    uv pip install --system -r requirements.txt

# ✅ Run the entire system (Logging Server + FastAPI + Gradio UI)
run:
    source .venv/bin/activate && \
    python logging_server.py & sleep 2 && \
    uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 & sleep 2 && \
    python gui.py && wait
