import React, { useState, useRef } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1048576).toFixed(1) + ' MB';
}

export default function VideoDetection() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
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
    }
  };

  const analyzeVideo = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await fetch(`${API}/predict-video`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError('Failed to analyze video. Ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page active" style={{ display: 'block', paddingTop: '64px' }}>
      <div className="detection-layout">
        <div className="page-header">
          <h2>&#127916; Video Detection</h2>
          <p>Upload a video to analyze sampled frames and determine if the content is AI-generated.</p>
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
              <div className="drop-icon">&#127916;</div>
              <div className="drop-title">{file ? file.name : 'Drop video here or click to browse'}</div>
              <div className="drop-sub">{file ? `${formatBytes(file.size)} • Ready to analyze` : 'Frames extracted and analyzed individually'}</div>
              {!file && (
                <div className="drop-formats">
                  <span className="format-tag">MP4</span>
                  <span className="format-tag">AVI</span>
                  <span className="format-tag">MOV</span>
                </div>
              )}
            </div>
            <input 
              type="file" 
              ref={fileInputRef} 
              accept=".mp4,.avi,.mov,.mkv" 
              onChange={handleFileChange} 
              style={{ display: 'none' }} 
            />
            <button 
              className="btn btn-primary" 
              style={{ width: '100%', marginTop: '1rem', justifyContent: 'center' }} 
              onClick={analyzeVideo} 
              disabled={!file || loading}
            >
              {loading ? 'Analyzing...' : '🔍 Analyze Video'}
            </button>
            {error && <div style={{ color: 'var(--fake)', marginTop: '1rem', fontSize: '0.875rem' }}>{error}</div>}
          </div>
          
          <div className="result-panel">
            {loading ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1rem', padding: '2rem 0' }}>
                <div className="spinner"></div>
                <div className="spinner-text">Extracting & analyzing frames...</div>
              </div>
            ) : result ? (
              <>
                <div className={`result-badge ${result.overall_label === 'real' ? 'real' : 'fake'} fade-in`}>
                  <div className="result-badge-icon">{result.overall_label === 'real' ? '✅' : '⚠️'}</div>
                  <div>
                    <div className="result-label">OVERALL VERDICT</div>
                    <div className="result-verdict">{result.overall_prediction}</div>
                  </div>
                </div>
                <div className="video-stats">
                  <div className="stat-card">
                    <div className="stat-value fake">{result.fake_percentage}%</div>
                    <div className="stat-label">AI-Generated Confidence</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value real">{result.real_percentage}%</div>
                    <div className="stat-label">Real Confidence</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value neutral">{result.total_frames_analyzed}</div>
                    <div className="stat-label">Frames Analyzed</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value neutral">{result.inference_time_ms}ms</div>
                    <div className="stat-label">Total Time</div>
                  </div>
                </div>
                <div>
                  <div className="confidence-header">
                    <span className="confidence-label">AI-Generated Confidence</span>
                    <span className="confidence-value">{result.fake_percentage}%</span>
                  </div>
                  <div className="confidence-bar-bg">
                    <div className="confidence-bar-fill fake" style={{ width: `${result.fake_percentage}%`, transition: 'width 1s' }}></div>
                  </div>
                </div>
              </>
            ) : (
              <div className="result-empty">
                <div className="result-empty-icon">🎬</div>
                <p>Upload a video and click Analyze<br/>to see frame-by-frame analysis here.</p>
              </div>
            )}
          </div>
        </div>
        
        {result && result.frames && (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem' }}>Analyzed Frames</h3>
            <p style={{ color: 'var(--text2)', fontSize: '0.85rem', marginBottom: '1rem' }}>Each frame was independently classified by the model.</p>
            <div className="frames-grid">
              {result.frames.map((f, i) => (
                <div className="frame-card" key={i} style={{ animationDelay: `${i * 0.05}s` }}>
                  <div className="frame-thumb">
                    {f.preview ? <img src={f.preview} alt="Frame" /> : <div className="frame-thumb-ph">🎞️</div>}
                  </div>
                  <div className="frame-info">
                    <div className="frame-time">Frame {f.frame_index} • {f.timestamp}s</div>
                    <div className={`frame-verdict ${f.label}`}>{f.prediction}</div>
                    <div className="frame-conf">{f.confidence}% confidence</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
