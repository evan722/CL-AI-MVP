from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from .wav2lip_runner import Wav2LipStreamer
import os
import shutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("static/index.html")

@app.post("/upload/")
async def upload_files(
    video: UploadFile = File(...),
    audio: UploadFile = File(...),
    timestamps: UploadFile = File(...)
):
    video_path = os.path.join(UPLOAD_DIR, "video.mp4")
    audio_path = os.path.join(UPLOAD_DIR, "audio.wav")
    timestamp_path = os.path.join(UPLOAD_DIR, "timestamps.txt")

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    with open(timestamp_path, "wb") as f:
        shutil.copyfileobj(timestamps.file, f)

    # Run Wav2Lip
    Wav2LipStreamer.run(video_path, audio_path)

    return {"status": "success", "video_path": video_path, "avatar_path": "static/avatar.mp4"}
