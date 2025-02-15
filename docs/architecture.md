# System Architecture

The architecture follows a modular design using FastAPI, Gradio, and a logging server.

```mermaid
graph TD;
    A[User Uploads Audio] -->|Gradio UI| B[FastAPI Backend];
    B -->|Preprocessing| C[Audio Processing Module];
    C -->|Transcription| D[Speech-to-Text Engine];
    D -->|Analysis| E[Compliance & Sentiment Analysis];
    E -->|Final Results| F[Gradio UI Displays Output];
    B -->|Logs| G[Logging Server];
