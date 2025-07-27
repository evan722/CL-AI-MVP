# MuseTalk Avatar App

A FastAPI-based web application for generating talking avatars from audio and face images using MuseTalk.

## Features

- 🎭 Generate talking avatars from face images and audio
- 🎬 Process video slides with audio narration
- 🌐 Web-based interface for easy file uploads
- ⚡ Real-time avatar generation
- 🔄 WebSocket support for streaming avatar videos

## Installation Options

### Option 1: Local Installation (Recommended)

This method installs MuseTalk directly on your Ubuntu system without Docker, avoiding path and dependency issues.

#### Prerequisites
- Ubuntu 18.04+ or similar Linux distribution
- Python 3.8+
- CUDA 11.8+ (optional, for GPU acceleration)
- At least 8GB RAM
- 10GB+ free disk space for models

#### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/evan722/CL-AI-MVP.git
   cd CL-AI-MVP
   ```

2. **Run the setup script:**
   ```bash
   ./setup_local.sh
   ```
   
   This script will:
   - Install system dependencies
   - Create a Python virtual environment
   - Install all required Python packages
   - Download all necessary AI models (~3-4GB)
   - Set up the directory structure

3. **Start the application:**
   ```bash
   ./start_local.sh
   ```

4. **Access the application:**
   - Open your browser to `http://localhost:8080`
   - Or access via your public IP: `http://YOUR_IP:8080`

#### Manual Local Installation

If you prefer to install manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install MuseTalk dependencies
pip install face-alignment soundfile transformers librosa einops omegaconf ffmpeg-python moviepy imageio

# Download models (this will take some time)
pip install huggingface-hub gdown
huggingface-cli download yzd-v/DWPose --local-dir musetalk/models/dwpose --include "dw-ll_ucoco_384.pth"
huggingface-cli download TMElyralab/MuseTalk --local-dir musetalk/models --include "musetalk/musetalk.json" "musetalk/pytorch_model.bin"

# Start the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Option 2: Docker Installation

#### Prerequisites
- Docker with GPU support
- NVIDIA Docker runtime (for GPU acceleration)

#### Build and Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/evan722/CL-AI-MVP.git
   cd CL-AI-MVP
   ```

2. **Build the Docker image:**
   ```bash
   sudo docker build -t cl-avatar .
   ```

3. **Run the container:**
   ```bash
   # With GPU support
   sudo docker run --rm -p 8080:8080 --gpus all cl-avatar
   
   # CPU only
   sudo docker run --rm -p 8080:8080 cl-avatar
   ```

## Usage

1. **Upload Files:**
   - **Face Image**: Upload a clear photo of the person's face
   - **Audio Narration**: Upload the audio file (.wav, .mp3, etc.)
   - **Video Slides**: Upload the presentation video (optional)
   - **Timestamps JSON**: Upload timing information (optional)

2. **Generate Avatar:**
   - Click "Upload & Generate Avatar"
   - Wait for processing (this may take several minutes)
   - View the generated talking avatar video

3. **Real-time Streaming:**
   - Use WebSocket connection for real-time avatar generation
   - Suitable for live applications

## API Endpoints

- `GET /`: Main web interface
- `POST /upload`: Upload files and generate avatar
- `WebSocket /ws/avatar/{uid}`: Real-time avatar streaming
- `GET /static/*`: Static file serving
- `GET /uploads/*`: Uploaded file access
- `GET /outputs/*`: Generated video access

## Model Information

The application uses several AI models:

- **MuseTalk**: Main talking head generation model
- **DWPose**: Human pose estimation for facial landmarks
- **Face Parsing**: Facial feature segmentation
- **Whisper**: Audio feature extraction
- **SD VAE**: Variational autoencoder for image processing

## Troubleshooting

### Common Issues

1. **Model files not found**: Ensure all models are downloaded correctly
2. **CUDA errors**: Check CUDA installation and GPU compatibility
3. **Memory errors**: Ensure sufficient RAM (8GB+ recommended)
4. **Path errors**: Use local installation if Docker has path issues

### Performance Tips

- Use GPU acceleration for faster processing
- Ensure sufficient disk space for temporary files
- Close other applications to free up memory
- Use smaller batch sizes if running into memory issues

## Development

### Project Structure
```
CL-AI-MVP/
├── app/                 # FastAPI application
│   ├── main.py         # Main application file
│   └── musetalk_runner.py  # MuseTalk interface
├── musetalk/           # MuseTalk implementation (fixed paths)
├── static/             # Web interface files
├── uploads/            # User uploaded files
├── outputs/            # Generated videos
├── setup_local.sh      # Local installation script
├── start_local.sh      # Start script for local installation
└── Dockerfile          # Docker build configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project builds upon MuseTalk by TMElyralab. Please refer to their original license terms.

## Credits

- **MuseTalk**: [TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk)
- **DWPose**: OpenMMLab pose estimation
- **Face Alignment**: Face detection and alignment
- **FastAPI**: Web framework for the API
