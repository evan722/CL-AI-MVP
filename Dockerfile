FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Avoid interactive prompts (timezone)
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
    TZ=Etc/UTC apt install -y tzdata && \
    apt install -y ffmpeg git curl && \
    apt clean

# Set working directory
WORKDIR /app

# Copy our fixed MuseTalk implementation
COPY musetalk ./musetalk

# Install MuseTalk dependencies
WORKDIR /app/musetalk
RUN pip install -r requirements.txt || true
# Install minimal dependencies that work
RUN pip install face-alignment soundfile transformers librosa einops omegaconf ffmpeg-python moviepy imageio

# Download the required models
RUN pip install --upgrade huggingface-hub gdown
RUN huggingface-cli download yzd-v/DWPose --local-dir models/dwpose --include "dw-ll_ucoco_384.pth" || true
RUN huggingface-cli download TMElyralab/MuseTalk --local-dir models --include "musetalk/musetalk.json" "musetalk/pytorch_model.bin" || true
RUN gdown --id 154JgKpzCPW82qINcVieuPH3fZ2e0P812 -O models/face-parse-bisent/79999_iter.pth || true
RUN curl -L https://download.pytorch.org/models/resnet18-5c106cde.pth -o models/face-parse-bisent/resnet18-5c106cde.pth || true

# Install MuseTalk as a package by adding the directory to PYTHONPATH
ENV PYTHONPATH="/app"

# Install your app dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p uploads outputs

# Copy your FastAPI app and frontend files
COPY app ./app
COPY static ./static
COPY uploads ./uploads

# Start FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
