from fastapi import FastAPI, UploadFile, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uuid, os, asyncio
from .musetalk_runner import MuseTalkStreamer

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/upload")
async def upload(video: UploadFile, audio: UploadFile, times: UploadFile):
    uid = uuid.uuid4().hex
    os.makedirs("uploads", exist_ok=True)
    for file, ext in [(video, "_video.mp4"), (audio, "_audio.wav"), (times, "_timestamps.json")]:
        path = os.path.join("uploads", uid + ext)
        with open(path, "wb") as f: f.write(await file.read())
    return {"id": uid}

@app.websocket("/ws/avatar/{uid}")
async def ws_avatar(ws: WebSocket, uid: str):
    await ws.accept()
    streamer = MuseTalkStreamer(audio_path=f"uploads/{uid}_audio.wav", face_img="static/avatar_face.jpg")
    await streamer.start()
    try:
        while True:
            await asyncio.sleep(0)  # yield
            frame = await streamer.next_frame()
            if frame:
                await ws.send_text(frame)
    finally:
        streamer.stop()
