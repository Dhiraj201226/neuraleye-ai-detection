<div align="center">
  <h1>🩺 MediGuide AI</h1>
  <p><i>An AI-Powered Health Assistant for Early Symptom Analysis.</i></p>
  <p><strong>Addressing SDG 3: Good Health and Well-Being</strong></p>

  [![React](https://img.shields.io/badge/Frontend-React.js-blue.svg)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
  [![Hugging Face](https://img.shields.io/badge/AI-Hugging_Face-FFA500.svg)](https://huggingface.co/)
</div>

<hr/>

## 📖 Project Objective
Many people ignore early symptoms of diseases, leading to delayed treatment and worsening health conditions. **MediGuide AI** acts as a virtual health assistant. Users can describe their symptoms in natural language, and the AI analyzes them to provide potential causes, a risk assessment (Low/Medium/High), recommended next steps, and preventive health tips.

> **Disclaimer:** This tool is for educational guidance only and is not a substitute for professional medical diagnosis.

## ✨ Features
- 🧠 **AI Symptom Checker**: Powered by Hugging Face's `Mistral-7B-Instruct`.
- ⚠️ **Health Risk Assessment**: Classifies symptoms by severity.
- 💬 **Conversational Interface**: Natural language input for user convenience.
- 🚑 **Emergency Alerts**: Recommends immediate medical attention for high-risk symptoms.
- 🎨 **Modern UI**: Clean, responsive frontend built with React and TailwindCSS.

## 🛠️ Technology Stack
- **Frontend**: React.js (Vite), TailwindCSS, Lucide Icons.
- **Backend**: FastAPI (Python), Uvicorn, Requests.
- **AI/NLP**: Hugging Face Inference API (`mistralai/Mistral-7B-Instruct-v0.3`).

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.8+
- Node.js & npm
- A free [Hugging Face](https://huggingface.co/) account and API Token.

### 2. Backend Setup
Navigate to the root directory and install dependencies:
```bash
pip install -r requirements.txt
```
Update the `.env` file with your Hugging Face token:
```env
HF_TOKEN=hf_your_actual_token_here
```
Run the backend server (from the root folder):
```bash
uvicorn backend.main:app --reload
```
*(The backend runs on `http://localhost:8000`)*

### 3. Frontend Setup
Open a new terminal and navigate to the frontend folder:
```bash
cd frontend
npm run dev
```
*(The frontend runs on `http://localhost:5173`)*

## 📸 Screenshots
*(Save your screenshots in the `screenshots/` folder and link them here)*
- Home Page & Symptom Input
- AI Risk Assessment Result

## 🔮 Future Scope
- Multi-language support for rural areas.
- Voice assistant integration.
- Booking appointments directly with local hospitals.
