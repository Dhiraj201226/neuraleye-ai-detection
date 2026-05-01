# NeuralEye — AI Generated Image Detection System

A full-stack web application that classifies images and videos as **REAL** or **AI-GENERATED** using a fine-tuned ResNet-50 deep learning model.

## Project Structure

```
ai-detector/
├── frontend/
│   └── index.html          # Complete single-file frontend (HTML/CSS/JS)
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/            # Temporary upload storage
│   └── model/
│       ├── train.py        # ResNet-50 training script
│       └── resnet_detector.pth   # Trained model weights (add yours here)
└── README.md
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
# Server runs at http://localhost:5000
```

### 2. Frontend

Simply open `frontend/index.html` in a browser.
Or serve it: `python -m http.server 8080` then visit http://localhost:8080

> **Demo Mode**: If the Flask backend isn't running, the frontend automatically switches to demo mode with simulated predictions.

## API Endpoints

### POST /predict-image
```bash
curl -X POST http://localhost:5000/predict-image \
  -F "test_image.jpg"
```
**Response:**
```json
{
  "success": true,
  "prediction": "AI-GENERATED",
  "label": "fake",
  "confidence": 91.4,
  "probabilities": { "real": 8.6, "fake": 91.4 },
  "inference_time_ms": 43.2
}
```

### POST /predict-video
```bash
curl -X POST http://localhost:5000/predict-video \
  -F "file=@your_video.mp4"
```

### GET /model-info
Returns architecture, dataset stats, and training history.

### GET /health
Health check and model status.

## Training Your Own Model

```bash
cd backend
# Prepare dataset:
# dataset/train/real/  (real images)
# dataset/train/fake/  (AI-generated images)
# dataset/val/real/
# dataset/val/fake/

python model/train.py \
  --data_dir ./dataset \
  --epochs 30 \
  --batch_size 32 \
  --lr 0.0001
# Saves model to model/resnet_detector.pth
```

## Model Architecture

- **Backbone**: ResNet-50 (pretrained on ImageNet)
- **Input**: 224×224 RGB images
- **Head**: Dropout(0.5) → Linear(2048, 256) → ReLU → Dropout(0.3) → Linear(256, 2)
- **Output**: Softmax probabilities [Real, AI-Generated]

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS, Chart.js |
| Backend | Python, Flask, Flask-CORS |
| ML | PyTorch, torchvision, ResNet-50 |
| Video | OpenCV (cv2) |
| Images | Pillow (PIL) |
