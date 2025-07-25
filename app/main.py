from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid, os, asyncio
from .musetalk_runner import run_musetalk, MuseTalkStreamer  # Ensure both are imported

app = FastAPI()

# Allow frontend JavaScript to connect to the API
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
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")  # ✅ Required

@app.get("/")
def index():
    return FileResponse("static/index.html")

# ✅ Upload endpoint that saves files AND returns the generated video
@app.post("/upload")
async def upload(video: UploadFile, audio: UploadFile, times: UploadFile, face: UploadFile):
    uid = uuid.uuid4().hex
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Save all files
    paths = {}
    for file, suffix in [(video, "_video.mp4"), (audio, "_audio.wav"),
                         (times, "_timestamps.json"), (face, "_face.jpg")]:
        path = os.path.join("uploads", uid + suffix)
        with open(path, "wb") as f:
            f.write(await file.read())
        paths[suffix] = path

    # Run MuseTalk to generate avatar video
    output_path = f"outputs/{uid}_avatar.mp4"
    run_musetalk(
        audio_path=paths["_audio.wav"],
        face_img=paths["_face.jpg"],
        output_path=output_path
    )

    return {
        "id": uid,
        "output_video": f"{uid}_avatar.mp4"
    }

# WebSocket streaming endpoint (optional use case)
@app.websocket("/ws/avatar/{uid}")
async def ws_avatar(ws: WebSocket, uid: str):
    await ws.accept()

    audio_path = f"uploads/{uid}_audio.wav"
    face_path = f"uploads/{uid}_face.jpg"  # ✅ Use user-provided face if exists

    if not os.path.exists(audio_path) or not os.path.exists(face_path):
        await ws.send_text("ERROR: Required file(s) not found.")
        await ws.close()
        return

    streamer = MuseTalkStreamer(audio_path=audio_path, face_img=face_path)
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
