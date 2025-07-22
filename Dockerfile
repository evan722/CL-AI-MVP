FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg git curl git-lfs libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Enable Git LFS and pull Wav2Lip
RUN git lfs install && \
    git clone https://huggingface.co/camenduru/Wav2Lip wav2lip && \
    cd wav2lip && git lfs pull

# Create working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose uploads for playback
RUN mkdir -p /app/uploads

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
