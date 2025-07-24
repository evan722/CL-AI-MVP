FROM pytorch/pytorch:2.0-cuda11.7-cudnn

RUN apt update && apt install -y ffmpeg git curl

WORKDIR /app
RUN git clone https://github.com/TMElyralab/MuseTalk.git musetalk
WORKDIR /app/musetalk && pip install -r requirements.txt && \
  pip install openmim && mim install mmengine mmcv mmdet mmpose whisper

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY static ./static
COPY uploads ./uploads

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
