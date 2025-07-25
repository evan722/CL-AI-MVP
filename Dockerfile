FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Avoid interactive prompts (timezone)
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
    TZ=Etc/UTC apt install -y tzdata && \
    apt install -y ffmpeg git curl && \
    apt clean

# Set working directory
WORKDIR /app

# Clone MuseTalk model
RUN git clone https://github.com/TMElyralab/MuseTalk.git musetalk

# Install MuseTalk dependencies
WORKDIR /app/musetalk
RUN pip install -r requirements.txt && \
    pip install openmim && \
    mim install mmengine mmcv mmdet mmpose whisper

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
