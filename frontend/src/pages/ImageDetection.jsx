import React, { useState, useRef } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1048576).toFixed(1) + ' MB';
}

export default function ImageDetection() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [reported, setReported] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      setResult(null);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setResult(null);
      setReported(false);
    }
  };

  const analyzeImage = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await fetch(`${API}/predict-image`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError('Failed to analyze image. Ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const reportToCommunity = async () => {
    if (!result) return;
    try {
      const res = await fetch(`${API}/submit-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: result.filename,
          prediction: result.prediction,
          confidence: result.confidence,
          image_base64: result.image_preview || ''
        })
      });
      if (res.ok) {
        setReported(true);
      }
    } catch (err) {
      console.error("Failed to report to community", err);
    }
  };

  return (
    <div className="page active" style={{ display: 'block', paddingTop: '64px' }}>
      <div className="detection-layout">
        <div className="page-header">
          <h2>&#128444; Image Detection</h2>
          <p>Upload an image to classify it as REAL or AI-GENERATED.</p>
        </div>
        <div className="detection-grid">
          <div>
            <div 
              className={`drop-zone ${isDragging ? 'dragging' : ''}`}
              onClick={() => fileInputRef.current.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="drop-icon">&#128444;</div>
              <div className="drop-title">{file ? file.name : 'Drop image here or click to browse'}</div>
              <div className="drop-sub">{file ? `${formatBytes(file.size)} • Ready to analyze` : 'Maximum file size: 50MB'}</div>
              {!file && (
                <div className="drop-formats">
                  <span className="format-tag">JPG</span>
                  <span className="format-tag">JPEG</span>
                  <span className="format-tag">PNG</span>
                  <span className="format-tag">WEBP</span>
                </div>
              )}
            </div>
            <input 
              type="file" 
              ref={fileInputRef} 
              accept=".jpg,.jpeg,.png,.webp" 
              onChange={handleFileChange} 
              style={{ display: 'none' }} 
            />
            <button 
              className="btn btn-primary" 
              style={{ width: '100%', marginTop: '1rem', justifyContent: 'center' }} 
              onClick={analyzeImage} 
              disabled={!file || loading}
            >
              {loading ? 'Analyzing...' : '🔍 Analyze Image'}
            </button>
            {error && <div style={{ color: 'var(--fake)', marginTop: '1rem', fontSize: '0.875rem' }}>{error}</div>}
          </div>
          
          <div className="result-panel">
            {loading ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1rem', padding: '3rem 0' }}>
                <div className="spinner"></div>
                <div className="spinner-text">Running inference...</div>
              </div>
            ) : result ? (
              <>
                {result.image_preview && (
                  <div className="preview-container">
                    <img src={result.image_preview} alt="preview" />
                  </div>
                )}
                <div className={`result-badge ${result.label === 'real' ? 'real' : 'fake'} fade-in`}>
                  <div className="result-badge-icon">{result.label === 'real' ? '✅' : '⚠️'}</div>
                  <div>
                    <div className="result-label">CLASSIFICATION RESULT</div>
                    <div className="result-verdict">{result.prediction}</div>
                  </div>
                </div>
                <div>
                  <div className="confidence-header">
                    <span className="confidence-label">Confidence Score</span>
                    <span className="confidence-value">{result.confidence}%</span>
                  </div>
                  <div className="confidence-bar-bg">
                    <div 
                      className={`confidence-bar-fill ${result.label === 'real' ? 'real' : 'fake'}`} 
                      style={{ width: `${result.confidence}%`, transition: 'width 1s' }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text2)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Probability Breakdown</div>
                  <div className="prob-row">
                    <div className="prob-name">Real</div>
                    <div className="prob-bar-bg">
                      <div className="prob-bar-real" style={{ width: `${result.probabilities?.real || 0}%`, transition: 'width 1s' }}></div>
                    </div>
                    <div className="prob-val">{result.probabilities?.real || 0}%</div>
                  </div>
                  <div className="prob-row">
                    <div className="prob-name">AI-Generated</div>
                    <div className="prob-bar-bg">
                      <div className="prob-bar-fake" style={{ width: `${result.probabilities?.fake || 0}%`, transition: 'width 1s' }}></div>
                    </div>
                    <div className="prob-val">{result.probabilities?.fake || 0}%</div>
                  </div>
                </div>
                <div className="meta-row">
                  <div className="meta-item">File: <span>{result.filename}</span></div>
                  <div className="meta-item">Inference: <span>{result.inference_time_ms}ms</span></div>
                  <div className="meta-item">Model: <span>Vision Transformer (ViT)</span></div>
                </div>
                {result.label === 'fake' && (
                  <button 
                    className="btn btn-secondary" 
                    onClick={reportToCommunity}
                    disabled={reported}
                    style={{ width: '100%', marginTop: '0.5rem', borderColor: reported ? 'var(--real)' : 'var(--fake)', color: reported ? 'var(--real)' : 'var(--fake)' }}
                  >
                    {reported ? '✅ Reported to Community' : '🚨 Report to Community Database'}
                  </button>
                )}
              </>
            ) : (
              <div className="result-empty">
                <div className="result-empty-icon">🤖</div>
                <p>Upload an image and click Analyze<br/>to see the prediction result here.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
