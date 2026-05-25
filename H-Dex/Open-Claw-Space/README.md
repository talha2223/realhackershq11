# Open Claw Agent (H-Dex)

This space hosts the Open Claw Agent API which processes natural language into JSON commands using Llama-3-8B.

## Setup Instructions
1. Upload these files to a new Hugging Face Space (Docker/FastAPI).
2. Go to **Settings > Secrets** in your space and add:
   - `HF_INFERENCE_TOKEN`: Your Hugging Face API key.
3. The Space will automatically run `uvicorn app:app` via the `Procfile`.
