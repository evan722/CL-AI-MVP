FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg git curl git-lfs libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Enable Git LFS before clone
RUN git lfs install && \
    git clone https://huggingface.co/camenduru/Wav2Lip wav2lip && \
    cd wav2lip && git lfs pull

# Create working directory
WORKDIR /app

# Copy your Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
