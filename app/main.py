from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid, os, asyncio

from .musetalk_runner import MuseTalkStreamer, run_musetalk

app = FastAPI()

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folders
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload(video: UploadFile, audio: UploadFile, timestamps: UploadFile, face: UploadFile):
    uid = uuid.uuid4().hex
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Save all uploaded files
    paths = {
        "video": os.path.join("uploads", f"{uid}_video.mp4"),
        "audio": os.path.join("uploads", f"{uid}_audio.wav"),
        "timestamps": os.path.join("uploads", f"{uid}_timestamps.json"),
        "face": os.path.join("uploads", f"{uid}_face.jpg")
    }
    for file, path in zip([video, audio, timestamps, face], paths.values()):
        with open(path, "wb") as f:
            f.write(await file.read())

    # Generate avatar video
    output_path = os.path.join("outputs", f"{uid}.mp4")
    run_musetalk(paths["audio"], paths["face"], output_path)

    return {
        "id": uid,
        "output_video": f"{uid}.mp4"
    }

@app.websocket("/ws/avatar/{uid}")
async def ws_avatar(ws: WebSocket, uid: str):
    await ws.accept()

    audio_path = f"uploads/{uid}_audio.wav"
    face_img_path = f"uploads/{uid}_face.jpg"

    if not os.path.exists(audio_path):
        await ws.send_text("ERROR: Audio file not found.")
        await ws.close()
        return

    streamer = MuseTalkStreamer(audio_path=audio_path, face_img=face_img_path)
    await streamer.start()

    try:
        while True:
            await asyncio.sleep(0)
            frame = await streamer.next_frame()
            if frame:
                await ws.send_text(frame)
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    finally:
        streamer.stop()
