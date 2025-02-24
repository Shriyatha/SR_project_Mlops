# *System Architecture Overview*

The architecture of this system follows a modular design that efficiently handles audio transcription, compliance analysis, and sentiment detection, while maintaining scalability and robustness. It is built using the following key components:

•⁠  ⁠*FastAPI*: For high-performance backend API interactions.

•⁠  ⁠*Gradio*: To provide a user-friendly interface for interaction.

•⁠  ⁠*Logging Server*: To capture and monitor system events for debugging and analysis.

---
## *System Architecture Diagram*

The following diagram illustrates the flow of data through the system:

```mermaid
graph LR;
  A[User Uploads Audio] -->|Gradio UI| B[FastAPI Backend];
  B -->|Validation| C[Audio Validation Module];
  C -->|Preprocessing| D[Audio Processing Module];
  D -->|Transcription| E[Speech-to-Text Engine];
  E -->|Cleaning| F[Text Cleaning Module];
  F -->|Compliance Check| G[Compliance Analysis];
  F -->|Prohibited Phrase Check| H[Profanity & PII Detection];
  F -->|Categorization| I[Call Categorization];
  F -->|Sentiment Analysis| J[Sentiment Detection];
  F -->|Speaking Speed Analysis| K[Speaking Speed Evaluation];
  D -->|Speaker Diarization| L[Speaker Diarization Module];
  G -->|Extract Timestamps| M[Timestamp Extraction];
  H -->|Mask PII & Profanity| N[Masking Module];
  G -->|Results| O[Final Compliance Report];
  I -->|Results| P[Category Report];
  J -->|Results| Q[Sentiment Report];
  K -->|Results| R[Speaking Speed Report];
  L -->|Results| S[Diarization Report];
  B -->|Logs| T[Logging Server];
  O & P & Q & R & S -->|Final Results| U[Gradio UI Displays Output];
```

---