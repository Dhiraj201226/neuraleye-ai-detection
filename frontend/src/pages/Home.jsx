import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="page active" id="page-home" style={{ display: 'block', paddingTop: '64px' }}>
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">Vision Transformer (ViT) &middot; PyTorch &middot; 99% Accuracy</div>
          <h1>Detect <span className="hl">AI-Generated</span><br/>Media Instantly</h1>
          <p>NeuralEye uses a fine-tuned Vision Transformer (ViT) neural network with self-attention mechanisms to distinguish authentic photographs from AI-synthesized images and videos with exceptional accuracy.</p>
          <div className="hero-buttons">
            <button className="btn btn-primary" onClick={() => navigate('/image')}>&#128444; Analyze Image</button>
            <button className="btn btn-secondary" onClick={() => navigate('/video')}>&#127916; Analyze Video</button>
          </div>
        </div>
      </section>

      <div className="features-strip">
        <div className="feature-item"><div className="feature-icon">&#9889;</div>Real-time Inference</div>
        <div className="feature-item"><div className="feature-icon">&#127919;</div>99% Test Accuracy</div>
        <div className="feature-item"><div className="feature-icon">&#128444;</div>Image + Video Support</div>
        <div className="feature-item"><div className="feature-icon">&#128302;</div>ViT Backbone</div>
        <div className="feature-item"><div className="feature-icon">&#128202;</div>Confidence Scores</div>
      </div>

      <section className="section">
        <div className="section-label">// HOW IT WORKS</div>
        <h2 className="section-title">From Upload to Verdict<br/>in Milliseconds</h2>
        <p className="section-sub">Our pipeline preprocesses your media, runs it through a trained neural network, and returns a classification with confidence scores.</p>
        <div className="steps-grid">
          <div className="step-card"><div className="step-number">01</div><div className="step-icon">&#128228;</div><div className="step-title">Upload Media</div><div className="step-desc">Drag and drop or select a JPG, PNG, or MP4 file. The system accepts images up to 50MB.</div></div>
          <div className="step-card"><div className="step-number">02</div><div className="step-icon">&#9881;</div><div className="step-title">Preprocessing</div><div className="step-desc">Images are resized to 224x224 and broken down into sequential 16x16 patches.</div></div>
          <div className="step-card"><div className="step-number">03</div><div className="step-icon">&#129504;</div><div className="step-title">ViT Inference</div><div className="step-desc">The Vision Transformer processes the image patches using multi-head self-attention.</div></div>
          <div className="step-card"><div className="step-number">04</div><div className="step-icon">&#128202;</div><div className="step-title">Results</div><div className="step-desc">Softmax probabilities are returned with REAL or AI-GENERATED verdict and a confidence score.</div></div>
        </div>
      </section>
    </div>
  );
}
