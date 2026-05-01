import React from 'react';
import loss_accuracy from "../assets/loss_accuracy.png";
import confusion_matrix from "../assets/confusion_matrix.png";
export default function ModelInfo() {
  return (
    <div className="page active" style={{ display: 'block', paddingTop: '64px' }}>
      <div className="detection-layout">
        <div className="page-header">
          <h2>🧠 Model Information</h2>
          <p>Technical details about the neural network architectures powering NeuralEye.</p>
        </div>
        
        <div className="insights-grid" style={{ marginTop: '0' }}>
          <div className="insight-card">
            <div className="insight-card-title">Training Configuration (Kaggle)</div>
            <div className="metrics-grid">
              <div className="metric-item">
                <div className="metric-val" style={{ fontSize: '1.2rem' }}>ResNet-50</div>
                <div className="metric-name">Architecture</div>
              </div>
              <div className="metric-item">
                <div className="metric-val">32</div>
                <div className="metric-name">Batch Size</div>
              </div>
              <div className="metric-item">
                <div className="metric-val">35</div>
                <div className="metric-name">Epochs</div>
              </div>
              <div className="metric-item">
              <div className="metric-val">0.0001</div>
              <div className="metric-name">Learning Rate</div>
            </div>
            <div className="metric-item">
              <div className="metric-val" style={{ fontSize: '1.2rem' }}>Adam</div>
              <div className="metric-name">Optimizer</div>
            </div>
            <div className="metric-item">
              <div className="metric-val" style={{ fontSize: '1rem' }}>CrossEntropy</div>
              <div className="metric-name">Loss Function</div>
            </div>
          </div>
        </div>

        <div className="insight-card">
          <div className="insight-card-title">Data Pipeline</div>
          <div className="arch-layers">
            <div className="arch-layer">
              <div className="arch-layer-icon">📐</div>
              <div>
                <div className="arch-layer-name">Input Resolution</div>
                <div className="arch-layer-desc">Resized to 256x256, center/random cropped to 224x224</div>
              </div>
            </div>
            <div className="arch-layer">
              <div className="arch-layer-icon">🔄</div>
              <div>
                <div className="arch-layer-name">Augmentations</div>
                <div className="arch-layer-desc">Random horizontal flip, random resized crop</div>
              </div>
            </div>
            <div className="arch-layer">
              <div className="arch-layer-icon">🧮</div>
              <div>
                <div className="arch-layer-name">Normalization</div>
                <div className="arch-layer-desc">Mean: [0.485, 0.456, 0.406], Std: [0.229, 0.224, 0.225]</div>
              </div>
            </div>
            <div className="arch-layer">
              <div className="arch-layer-icon">🎯</div>
              <div>
                <div className="arch-layer-name">Classes</div>
                <div className="arch-layer-desc">2 Classes: Real (0) vs AI-Generated/Fake (1)</div>
              </div>
            </div>
          </div>
        </div>
      </div>

        <div className="result-panel" style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem' }}>Dual-Model Architecture</h3>
          <p style={{ color: 'var(--text2)', lineHeight: '1.7', marginBottom: '1.5rem' }}>
            NeuralEye utilizes a flexible dual-model architecture to ensure robustness and high accuracy. 
            Depending on the deployment environment and available resources, the system routes inference to one of two models:
          </p>
          
          <div className="steps-grid" style={{ marginTop: '0' }}>
            <div className="step-card" style={{ padding: '1.5rem' }}>
              <div className="step-number">PRIMARY</div>
              <div className="step-title" style={{ fontSize: '1.2rem' }}>Vision Transformer (ViT)</div>
              <div className="step-desc" style={{ marginTop: '0.5rem' }}>
                Deployed via Hugging Face pipeline (<code>haywoodsloan/ai-image-detector-deploy</code>). 
                Uses multi-head self-attention mechanisms to analyze images in 16x16 sequential patches. 
                Highly accurate at detecting subtle generative artifacts that CNNs might miss.
              </div>
            </div>
            
            <div className="step-card" style={{ padding: '1.5rem' }}>
              <div className="step-number">SECONDARY</div>
              <div className="step-title" style={{ fontSize: '1.2rem' }}>ResNet-50</div>
              <div className="step-desc" style={{ marginTop: '0.5rem' }}>
                A custom PyTorch model trained locally on Kaggle GPUs. 
                ResNet-50 utilizes deep residual learning with 50 layers to combat the vanishing gradient problem. 
                Chosen for its robust feature extraction capabilities and proven track record in deepfake detection.
              </div>
            </div>
          </div>
        </div>

        <div className="result-panel" style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem' }}>Performance Metrics</h3>
          <p style={{ color: 'var(--text2)', lineHeight: '1.7', marginBottom: '1.5rem' }}>
            Below are the training performance visualisations including the Loss Graph and the Confidence Matrix. 
            (Please ensure your image files are named <code>loss_accuracy.png</code> and <code>confusion_matrix.png</code> and placed in the <code>public</code> directory).
          </p>
          
          <div className="detection-grid" style={{ marginTop: '1rem' }}>
            <div className="insight-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="insight-card-title" style={{ width: '100%' }}>Training & Validation Loss</div>
              <img 
                src={loss_accuracy}
                alt="Loss Graph" 
                style={{ width: '100%',height:'250px', borderRadius: '8px', border: '1px solid var(--border)' }}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div style={{ display: 'none', width: '100%', height: '250px', background: 'var(--bg3)', borderRadius: '8px', alignItems: 'center', justifyContent: 'center', color: 'var(--text3)', border: '1px dashed var(--border-bright)' }}>
                [loss_graph.png not found in public folder]
              </div>
            </div>
            
            <div className="insight-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="insight-card-title" style={{ width: '100%' }}>Confidence Matrix</div>
              <img 
                src={confusion_matrix}
                alt="Confidence Matrix" 
                style={{ width: '100%', height:'250px', borderRadius: '8px', border: '1px solid var(--border)' }}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div style={{ display: 'none', width: '100%', height: '250px', background: 'var(--bg3)', borderRadius: '8px', alignItems: 'center', justifyContent: 'center', color: 'var(--text3)', border: '1px dashed var(--border-bright)' }}>
                [confusion_matrix.png not found in public folder]
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
