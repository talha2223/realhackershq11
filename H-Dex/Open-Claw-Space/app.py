"""
Open Claw AI Agent - Hugging Face Space
Handles natural language parsing for H-Dex infrastructure using Llama-3/Mistral via HF Inference API.
"""
import os
import json
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from huggingface_hub import InferenceClient

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OpenClaw")

app = FastAPI(title="Open Claw Agent", version="1.0")

# Pull token from Environment (Hugging Face Space Secrets)
HF_TOKEN = os.environ.get("HF_INFERENCE_TOKEN")
if not HF_TOKEN:
    logger.warning("HF_INFERENCE_TOKEN is not set. API calls will fail.")

# We use the free serverless API for Meta Llama 3 or Mistral
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct" 

try:
    client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)
except Exception as e:
    logger.error(f"Failed to init InferenceClient: {e}")
    client = None

# Custom System Prompt that gives the AI identity and instructions on JSON tool usage
SYSTEM_PROMPT = """You are Open Claw, the autonomous AI administrator for the H-Dex infrastructure.
Your job is to assist human operators in managing their remote nodes. 
When asked to perform a computer action, output a JSON command block meant for the Bot API.
Otherwise, respond concisely and professionally as a brilliant system administrator."""

@app.get("/")
def read_root():
    return {"status": "Open Claw is awake & listening."}

@app.post("/api/ask")
async def ask_claw(request: Request):
    """
    Main endpoint for the Discord Bot and Web Dashboard to ping for AI insights.
    Expects json: {"prompt": "User's query", "context": "Optional system state/telemetry JSON"}
    """
    if not client:
        raise HTTPException(status_code=500, detail="Inference Client not available (Token missing or rate limited).")
        
    try:
        data = await request.json()
        user_prompt = data.get("prompt", "")
        telemetry = data.get("context", "")
        
        # Build the conversation for the chat context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        if telemetry:
            messages.append({"role": "system", "content": f"CURRENT TELEMETRY CONTEXT:\\n{telemetry}"})
            
        messages.append({"role": "user", "content": user_prompt})
        
        # Call Hugging Face API
        response = client.chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.2, # Low temp for precise, technical answers
        )
        
        ai_reply = response.choices[0].message.content
        
        return JSONResponse(content={"reply": ai_reply, "success": True})
        
    except Exception as e:
        logger.error(f"Error in ask_claw: {e}")
        return JSONResponse(status_code=500, content={"reply": f"Internal Error: {str(e)}", "success": False})

# Note: In Hugging Face spaces, the app is automatically run by uvicorn.
