import React, { useState } from 'react';
import axios from 'axios';
import { Activity, AlertTriangle, Send, Loader2, Info } from 'lucide-react';

function App() {
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyzeSymptoms = async () => {
    if (!symptoms.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: symptoms
      });
      
      const rawText = response.data.response;
      setResult(rawText);
    } catch (err) {
      console.error(err);
      setError('Failed to analyze symptoms. Ensure the backend is running and your Hugging Face API key is correct in the .env file.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (text) => {
    if (!text) return 'bg-white';
    const lower = text.toLowerCase();
    if (lower.includes('high')) return 'bg-red-50 border-red-500 text-red-900';
    if (lower.includes('medium')) return 'bg-yellow-50 border-yellow-500 text-yellow-900';
    if (lower.includes('low')) return 'bg-green-50 border-green-500 text-green-900';
    return 'bg-blue-50 border-blue-500 text-blue-900';
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-600">
            <Activity size={28} className="stroke-[2.5]" />
            <h1 className="text-xl font-bold tracking-tight text-slate-800">MediGuide AI</h1>
          </div>
          <div className="text-xs font-semibold text-blue-700 bg-blue-100 px-3 py-1.5 rounded-full uppercase tracking-wider">
            SDG 3: Good Health
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 flex flex-col md:flex-row gap-8">
        
        <div className="w-full md:w-1/2 flex flex-col gap-4">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-2">Describe your symptoms</h2>
            <p className="text-sm text-slate-500 mb-4">
              Please provide as much detail as possible. E.g., "I have had a severe headache and fever for 2 days."
            </p>
            
            <textarea 
              className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none resize-none text-slate-700"
              rows={6}
              placeholder="I am experiencing..."
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
            />
            
            <button 
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 px-4 rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-70 disabled:hover:bg-blue-600 shadow-sm shadow-blue-200"
              onClick={analyzeSymptoms}
              disabled={loading || !symptoms.trim()}
            >
              {loading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
              {loading ? 'Analyzing...' : 'Analyze Symptoms'}
            </button>
          </div>

          <div className="bg-blue-50 p-5 rounded-2xl border border-blue-100 flex gap-3 text-blue-800 text-sm shadow-sm">
            <Info className="shrink-0 mt-0.5" size={20} />
            <p><strong>Disclaimer:</strong> MediGuide AI is for educational purposes and initial guidance only. It is not a substitute for professional medical advice, diagnosis, or treatment.</p>
          </div>
        </div>

        <div className="w-full md:w-1/2">
          {error && (
            <div className="bg-red-50 p-5 rounded-2xl border border-red-200 text-red-700 flex gap-3 items-start shadow-sm mb-4">
              <AlertTriangle className="shrink-0 mt-0.5" size={20} />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {!result && !error && !loading && (
            <div className="h-full bg-white border-2 border-slate-200 border-dashed rounded-2xl flex flex-col items-center justify-center text-center p-8 min-h-[400px]">
              <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mb-4">
                <Activity size={32} />
              </div>
              <h3 className="text-lg font-bold text-slate-800">No Symptoms Analyzed</h3>
              <p className="text-slate-500 text-sm mt-2 max-w-[250px]">Enter your symptoms on the left to receive an AI-powered health assessment.</p>
            </div>
          )}

          {loading && (
            <div className="h-full bg-white border border-slate-100 rounded-2xl flex flex-col items-center justify-center p-8 min-h-[400px] shadow-sm">
              <Loader2 className="animate-spin text-blue-600 mb-4" size={40} />
              <h3 className="text-lg font-bold text-slate-800 animate-pulse">Consulting AI Model...</h3>
              <p className="text-slate-500 text-sm mt-2">Connecting to Hugging Face Inference API.</p>
            </div>
          )}

          {result && !loading && (
            <div className={`rounded-2xl shadow-sm border-l-4 p-6 min-h-[400px] ${getRiskColor(result)}`}>
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2 border-b border-current pb-4 border-opacity-20">
                <Activity size={24} />
                Assessment Results
              </h2>
              <div className="whitespace-pre-wrap text-sm leading-relaxed font-medium">
                {result}
              </div>
            </div>
          )}
        </div>
        
      </main>
    </div>
  );
}

export default App;
