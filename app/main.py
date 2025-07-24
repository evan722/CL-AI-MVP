from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid, os, asyncio
from .musetalk_runner import MuseTalkStreamer

app = FastAPI()

# Allow frontend JavaScript to connect to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and uploads directories
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve the HTML frontend
@app.get("/")
def index():
    return FileResponse("static/index.html")

# Upload endpoint for video, audio, timestamps
@app.post("/upload")
async def upload(video: UploadFile, audio: UploadFile, times: UploadFile):
    uid = uuid.uuid4().hex
    os.makedirs("uploads", exist_ok=True)
    for file, suffix in [(video, "_video.mp4"), (audio, "_audio.wav"), (times, "_timestamps.json")]:
        path = os.path.join("uploads", uid + suffix)
        with open(path, "wb") as f:
            f.write(await file.read())
    return {"id": uid}

# WebSocket endpoint for real-time avatar streaming
@app.websocket("/ws/avatar/{uid}")
async def ws_avatar(ws: WebSocket, uid: str):
    await ws.accept()

    # Optional: validate that file exists
    audio_path = f"uploads/{uid}_audio.wav"
    if not os.path.exists(audio_path):
        await ws.send_text("ERROR: Audio file not found.")
        await ws.close()
        return

    # Default face image
    face_img_path = "static/avatar_face.jpg"

    streamer = MuseTalkStreamer(audio_path=audio_path, face_img=face_img_path)
    await streamer.start()

    try:
        while True:
            await asyncio.sleep(0)  # let event loop run
            frame = await streamer.next_frame()
            if frame:
                await ws.send_text(frame)
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    finally:
        streamer.stop()
