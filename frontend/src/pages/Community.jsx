import React, { useState, useEffect } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Community() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const res = await fetch(`${API}/community-reports`);
        if (!res.ok) throw new Error('Failed to fetch');
        const data = await res.json();
        setReports(data);
      } catch (err) {
        console.error("Error fetching community reports:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  return (
    <div className="page active" style={{ display: 'block', paddingTop: '64px' }}>
      <div className="section" style={{ padding: '3rem 2rem' }}>
        <div className="page-header">
          <h2>🌐 Community Warning Gallery</h2>
          <p>A live feed of confirmed AI-generated media reported by our community to help stop the spread of misinformation.</p>
        </div>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem 0' }}>
            <div className="spinner"></div>
          </div>
        ) : reports.length === 0 ? (
          <div className="result-empty" style={{ background: 'var(--bg2)', padding: '4rem 2rem', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)' }}>
            <div className="result-empty-icon">🛡️</div>
            <p>No community reports yet.<br/>Be the first to report an AI-generated image!</p>
          </div>
        ) : (
          <div className="community-grid">
            {reports.map((report) => (
              <div key={report.id} className="report-card fade-in">
                <div className="report-img-wrapper">
                  <div className="report-badge">AI-GENERATED</div>
                  {report.image_base64 ? (
                    <img src={report.image_base64} alt={report.filename} />
                  ) : (
                    <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.5 }}>No Preview</div>
                  )}
                </div>
                <div className="report-info">
                  <div className="report-filename" title={report.filename}>{report.filename}</div>
                  <div className="report-meta">
                    <span className="report-conf">{report.confidence}% Confidence</span>
                    <span>{new Date(report.timestamp).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
