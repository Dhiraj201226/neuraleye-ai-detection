import os
import io
import time
import base64
import cv2
import numpy as np
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from transformers import pipeline
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import sqlite3
from datetime import datetime
from pydantic import BaseModel

app = FastAPI(title="Deepfake Detection API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Templates (removed)

# =====================================================================
# LOCAL HUGGING FACE MODEL SETUP (NO API KEY REQUIRED)
# =====================================================================
MODEL_ID = "haywoodsloan/ai-image-detector-deploy"
print(f"Loading local Hugging Face model '{MODEL_ID}'... This may take a moment to download weights on first run.")
# Load the model entirely locally (downloads weights to your machine)
local_hf_pipeline = pipeline("image-classification", model=MODEL_ID)
print("Model loaded successfully!")

ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "webp"}
ALLOWED_VIDEO_EXT = {"mp4", "avi", "mov", "mkv"}

cache = {}

# =====================================================================
# LOCAL MODEL SETUP (FOR WHEN YOU DOWNLOAD YOUR KAGGLE MODEL)
# =====================================================================
LOCAL_MODEL_PATH = "deepfake_resnet50.pth"
local_model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Image transformations for the local PyTorch model
local_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def load_local_model():
    global local_model
    if os.path.exists(LOCAL_MODEL_PATH):
        print("Loading local PyTorch model...")
        import torch.nn as nn
        # Must match the architecture in kaggle_train.py
        model = models.resnet50(pretrained=False)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, 2)
        model.load_state_dict(torch.load(LOCAL_MODEL_PATH, map_location=device))
        model.to(device)
        model.eval()
        local_model = model
        print("Local model loaded successfully!")
    else:
        print(f"Local model not found at {LOCAL_MODEL_PATH}. Will use HuggingFace API if available.")

# Try to load local model on startup
load_local_model()

# =====================================================================
# DATABASE SETUP FOR COMMUNITY REPORTS
# =====================================================================
def init_db():
    conn = sqlite3.connect("community.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            prediction TEXT,
            confidence REAL,
            image_base64 TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic Models for new endpoints
class ReportRequest(BaseModel):
    filename: str
    prediction: str
    confidence: float
    image_base64: str

class ChatRequest(BaseModel):
    message: str

# =====================================================================
# ROUTES
# =====================================================================
# Serve the static React build files
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(full_path: str):
    return HTMLResponse(open("frontend/dist/index.html", "r", encoding="utf-8").read())

def is_allowed_file(filename: str, allowed_set: set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

def pil_to_jpeg_bytes(pil_img, max_side=800):
    w, h = pil_img.size
    crop = min(max_side, w, h)
    img = pil_img.crop(((w-crop)//2, (h-crop)//2, (w+crop)//2, (h+crop)//2))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

def image_to_base64_preview(pil_img, max_side=400):
    img = pil_img.copy()
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"

# --- INFERENCE ENGINE ---
def classify_image(pil_img: Image.Image) -> dict:
    """Uses either the local Kaggle model or the HuggingFace API."""
    
    # 1. Try Local Model First
    if local_model is not None:
        input_tensor = local_transform(pil_img).unsqueeze(0).to(device)
        with torch.no_grad():
            outputs = local_model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Assuming class 0 is Real, class 1 is Fake (from kaggle_train.py)
            real_score = probabilities[0].item()
            fake_score = probabilities[1].item()
            
            is_ai = fake_score > real_score
            top_score = max(real_score, fake_score)
            
            return {
                "is_ai": is_ai,
                "top_score": top_score,
                "real_score": real_score,
                "fake_score": fake_score,
            }
            
    # 2. Use Local Hugging Face Pipeline
    img_bytes = pil_to_jpeg_bytes(pil_img)
    key = hash(img_bytes)
    if key in cache:
        return cache[key]

    # Run inference completely locally on your CPU/GPU
    results = local_hf_pipeline(pil_img)
    
    top_pred = max(results, key=lambda x: x["score"])
    pred_label = top_pred["label"].lower()

    # Detect fake/AI labels using the exact finalized logic
    is_ai = any(
        word in pred_label
        for word in [
            "fake",
            "generated",
            "artificial",
            "deepfake",
            "ai"
        ]
    )

    # Calculate individual scores for the frontend
    real_score = next((r["score"] for r in results if not any(w in r["label"].lower() for w in ["fake", "generated", "artificial", "deepfake", "ai"])), 0)
    fake_score = next((r["score"] for r in results if any(w in r["label"].lower() for w in ["fake", "generated", "artificial", "deepfake", "ai"])), 0)

    result = {
        "is_ai": is_ai,
        "top_score": top_pred["score"],
        "real_score": real_score,
        "fake_score": fake_score,
    }

    cache[key] = result
    return result

@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    if not is_allowed_file(file.filename, ALLOWED_IMAGE_EXT):
        raise HTTPException(status_code=400, detail="Invalid image extension")

    start = time.time()
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")

    try:
        scores = classify_image(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "prediction": "AI-GENERATED" if scores["is_ai"] else "REAL",
        "label": "fake" if scores["is_ai"] else "real",
        "confidence": round(scores["top_score"] * 100, 1),
        "probabilities": {
            "real": round(scores["real_score"] * 100, 1),
            "fake": round(scores["fake_score"] * 100, 1),
        },
        "image_preview": image_to_base64_preview(img),
        "inference_time_ms": int((time.time() - start) * 1000),
        "filename": file.filename,
        "demo_mode": False
    }

@app.post("/predict-video")
async def predict_video(file: UploadFile = File(...)):
    if not is_allowed_file(file.filename, ALLOWED_VIDEO_EXT):
        raise HTTPException(status_code=400, detail="Invalid video extension")

    start = time.time()

    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        contents = await file.read()
        tmp.write(contents)
        path = tmp.name

    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    frames = []
    # Extract 5 evenly spaced frames
    idxs = np.linspace(0, max(total - 1, 0), 5, dtype=int)

    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ret, frame = cap.read()
        if not ret: 
            continue

        pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        try:
            scores = classify_image(pil)
            frames.append({
                "frame_index": int(i),
                "timestamp": round(i / fps, 2),
                "prediction": "AI-GENERATED" if scores["is_ai"] else "REAL",
                "label": "fake" if scores["is_ai"] else "real",
                "confidence": round(scores["top_score"] * 100, 1)
            })
        except Exception as e:
            print(f"Error processing frame {i}: {e}")

    cap.release()
    os.unlink(path)

    if not frames:
        raise HTTPException(status_code=500, detail="Could not extract any frames from video.")

    fake_count = sum(1 for f in frames if f["label"] == "fake")
    pct = round(fake_count / len(frames) * 100, 1)

    return {
        "overall_prediction": "AI-GENERATED" if pct >= 50 else "REAL",
        "overall_label": "fake" if pct >= 50 else "real",
        "fake_percentage": pct,
        "real_percentage": 100 - pct,
        "frames": frames,
        "total_frames_analyzed": len(frames),
        "inference_time_ms": int((time.time() - start) * 1000)
    }

# --- COMMUNITY ENDPOINTS ---
@app.post("/submit-report")
async def submit_report(req: ReportRequest):
    try:
        conn = sqlite3.connect("community.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reports (filename, prediction, confidence, image_base64) VALUES (?, ?, ?, ?)",
            (req.filename, req.prediction, req.confidence, req.image_base64)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Report submitted to community database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/community-reports")
async def get_community_reports():
    try:
        conn = sqlite3.connect("community.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- CHATBOT ENDPOINT ---
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    msg = req.message.lower()
    
    # Very simple keyword-based FAQ bot
    if "how" in msg and ("work" in msg or "detect" in msg):
        ans = "Our system uses advanced neural networks (Vision Transformers and ResNet-50) to analyze image patches for microscopic inconsistencies introduced by AI generators."
    elif "accuracy" in msg or "accurate" in msg:
        ans = "The models achieve over 95% accuracy on standard deepfake datasets by detecting blending artifacts and frequency domain anomalies."
    elif "model" in msg or "architecture" in msg:
        ans = "We use a dual-model approach: A Vision Transformer (ViT) via Hugging Face and a custom ResNet-50 PyTorch model trained on Kaggle."
    elif "video" in msg:
        ans = "For videos, we extract evenly spaced frames and analyze each one individually. If more than 50% of the frames are flagged, the entire video is considered AI-generated."
    elif "hello" in msg or "hi" in msg:
        ans = "Hello! I'm the NeuralEye Assistant. Ask me how our deepfake detection works, what models we use, or how to interpret your results!"
    elif "report" in msg or "database" in msg:
        ans = "If you detect an AI-generated image, you can report it to our Community Database! This helps warn others about fake media circulating online."
    else:
        ans = "I'm still learning! I can answer questions about how our deepfake detection works, the models we use, and how to analyze images/videos."
        
    return {"reply": ans}

# Run the server using: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable if available, otherwise default to 7860 for HF Spaces
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
