from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MediGuide AI API")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HF_TOKEN")
# Using Mistral as recommended
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat(req: ChatRequest):
    if not HF_TOKEN or HF_TOKEN == "hf_your_token_here":
        raise HTTPException(status_code=500, detail="Hugging Face API token is missing or invalid. Please update your .env file.")

    # Crafting a strong prompt for the Mistral Instruct model
    prompt = f"""<s>[INST] You are MediGuide AI, a professional health assistant. Analyze the user's symptoms and provide structured guidance. Do NOT provide a full medical diagnosis, just guidance.

Return EXACTLY in this format (do not add extra text outside this format):
Possible Causes:
- [cause 1]
- [cause 2]

Risk Level:
[Low/Medium/High]

Recommended Action:
[action]

Health Tips:
- [tip 1]
- [tip 2]

Symptoms:
{req.message} [/INST]"""

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 250,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
        )
        
        response.raise_for_status()
        data = response.json()
        
        # The Inference API returns a list of dictionaries
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return {"response": data[0]["generated_text"].strip()}
        else:
            return {"response": "Error: Unexpected format from AI.", "raw": data}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
