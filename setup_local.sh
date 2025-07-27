#!/bin/bash

# MuseTalk Local Installation Script
# This script sets up MuseTalk directly on Ubuntu without Docker

set -e  # Exit on any error

echo "🚀 Setting up MuseTalk Avatar App locally..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt install -y ffmpeg git curl python3-pip python3-venv

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install basic dependencies
echo "📚 Installing basic Python dependencies..."
pip install fastapi uvicorn python-multipart
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install MuseTalk dependencies
echo "🎭 Installing MuseTalk dependencies..."
pip install face-alignment soundfile transformers librosa einops omegaconf ffmpeg-python moviepy imageio
pip install opencv-python scikit-image tifffile
pip install numpy scipy scikit-learn numba

# Install additional dependencies
pip install mmengine --no-deps || echo "⚠️  mmengine installation failed, continuing..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs
mkdir -p musetalk/models/dwpose
mkdir -p musetalk/models/musetalk
mkdir -p musetalk/models/face-parse-bisent
mkdir -p musetalk/models/whisper

# Download models
echo "⬇️  Downloading required models..."

# Install huggingface hub for downloading
pip install huggingface-hub gdown

# Download DWPose model
echo "⬇️  Downloading DWPose model..."
huggingface-cli download yzd-v/DWPose --local-dir musetalk/models/dwpose --include "dw-ll_ucoco_384.pth"

# Download MuseTalk models
echo "⬇️  Downloading MuseTalk models..."
huggingface-cli download TMElyralab/MuseTalk --local-dir musetalk/models --include "musetalk/musetalk.json" "musetalk/pytorch_model.bin"

# Download face parsing models
echo "⬇️  Downloading face parsing models..."
mkdir -p musetalk/models/face-parse-bisent
gdown --id 154JgKpzCPW82qINcVieuPH3fZ2e0P812 -O musetalk/models/face-parse-bisent/79999_iter.pth
curl -L https://download.pytorch.org/models/resnet18-5c106cde.pth -o musetalk/models/face-parse-bisent/resnet18-5c106cde.pth

# Download SD VAE model
echo "⬇️  Downloading SD VAE model..."
mkdir -p musetalk/models/sd-vae
huggingface-cli download stabilityai/sd-vae-ft-mse --local-dir musetalk/models/sd-vae --include "config.json" "diffusion_pytorch_model.bin"

echo "✅ Installation complete!"
echo ""
echo "🎉 To start the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the server: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080"
echo "3. Open your browser to: http://localhost:8080"
echo ""
echo "📝 Note: The application will use CPU by default. For GPU acceleration,"
echo "   make sure you have CUDA installed and configured properly."