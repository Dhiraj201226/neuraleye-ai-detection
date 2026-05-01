import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ImageDetection from './pages/ImageDetection';
import VideoDetection from './pages/VideoDetection';
import ModelInfo from './pages/ModelInfo';
import Community from './pages/Community';
import Chatbot from './components/Chatbot';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/image" element={<ImageDetection />} />
        <Route path="/video" element={<VideoDetection />} />
        <Route path="/model-info" element={<ModelInfo />} />
        <Route path="/community" element={<Community />} />
      </Routes>
      <Chatbot />
      <footer>NeuralEye &middot; AI Generated Image Detection System &middot; Vision Transformer (ViT) &middot; PyTorch &middot; FastAPI</footer>
    </>
  );
}

export default App;
