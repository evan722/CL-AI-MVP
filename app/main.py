from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import asyncio

# Import the runner either as a package or module so the app can be executed
# both via ``uvicorn app.main:app`` and ``python app/main.py``/``streamlit run``
try:
    from .musetalk_runner import run_musetalk, stream_musetalk
except ImportError:  # pragma: no cover - fallback for script execution
    from musetalk_runner import run_musetalk, stream_musetalk


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
async def upload(video: UploadFile, audio: UploadFile, timestamps: UploadFile, avatar: UploadFile):
    uid = uuid.uuid4().hex
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Save all uploaded files
    paths = {
        "slides": os.path.join("uploads", f"{uid}_slides.mp4"),
        "audio": os.path.join("uploads", f"{uid}_audio.wav"),
        "timestamps": os.path.join("uploads", f"{uid}_timestamps.json"),
        "avatar": os.path.join("uploads", f"{uid}_avatar{os.path.splitext(avatar.filename)[1] or '.mp4'}"),
    }
    for file, path in zip([video, audio, timestamps, avatar], paths.values()):
        with open(path, "wb") as f:
            f.write(await file.read())

    # Generate avatar video
    output_path = os.path.join("outputs", f"{uid}.mp4")
    run_musetalk(paths["audio"], paths["avatar"], output_path)

    return {
        "id": uid,
        "output_video": f"{uid}.mp4",
        "slides_video": os.path.basename(paths["slides"]),
        "timestamps": os.path.basename(paths["timestamps"])
    }


@app.websocket("/ws/avatar/{uid}")
async def ws_avatar(ws: WebSocket, uid: str):
    await ws.accept()

    audio_path = os.path.join("uploads", f"{uid}_audio.wav")
    avatar_path = None
    for ext in [".mp4", ".jpg", ".png"]:
        p = os.path.join("uploads", f"{uid}_avatar{ext}")
        if os.path.exists(p):
            avatar_path = p
            break

    if not avatar_path or not os.path.exists(audio_path):
        await ws.send_text("ERROR: files missing")
        await ws.close()
        return

    streamer = stream_musetalk(audio_path, avatar_path)

    try:
        async for frame in streamer:
            await ws.send_text(frame)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await ws.send_text(f"ERROR: {exc}")
    finally:
        if hasattr(streamer, "aclose"):
            await streamer.aclose()
