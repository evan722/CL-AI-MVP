import os, uuid, aiofiles, json, asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketState
from .wav2lip_runner import Wav2LipStreamer

# ------------------ Setup ------------------

ROOT = Path(__file__).parent.parent
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True, parents=True)

app = FastAPI()

# Mount static and uploaded content
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")

# ------------------ Routes ------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return (ROOT / "static" / "index.html").read_text()

@app.post("/upload")
async def upload(video: UploadFile, audio: UploadFile, times: UploadFile):
    uid = uuid.uuid4().hex
    vpath = UPLOADS / f"{uid}_video.mp4"
    apath = UPLOADS / f"{uid}_audio.wav"
    tpath = UPLOADS / f"{uid}_timestamps.json"

    # Save all uploaded files
    async with aiofiles.open(vpath, "wb") as f:
        while chunk := await video.read(1 << 20):
            await f.write(chunk)

    async with aiofiles.open(apath, "wb") as f:
        while chunk := await audio.read(1 << 20):
            await f.write(chunk)

    async with aiofiles.open(tpath, "wb") as f:
        await f.write(await times.read())

    return {"id": uid}

# ------------------ WebSocket ------------------

active_streams: dict[str, Wav2LipStreamer] = {}

@app.websocket("/ws/avatar/{uid}")
async def avatar_ws(ws: WebSocket, uid: str):
    await ws.accept()
    streamer = None

    try:
        audio_file = UPLOADS / f"{uid}_audio.wav"
        if not audio_file.exists():
            await ws.close(code=4000)
            return

        streamer = Wav2LipStreamer(str(audio_file))
        active_streams[uid] = streamer
        asyncio.create_task(streamer.run())

        while True:
            if ws.application_state != WebSocketState.CONNECTED:
                break

            # Send frame if playing
            if streamer.play.is_set():
                frame = await streamer.next_frame()
                if frame:
                    await ws.send_text(frame)

            # Handle commands
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=0.01)
                cmd = json.loads(data)
                if cmd["action"] == "play":
                    streamer.play.set()
                elif cmd["action"] == "pause":
                    streamer.play.clear()
                elif cmd["action"] == "seek":
                    streamer.seek(cmd["t"])
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print("WebSocket command error:", e)
                break

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {uid}")
    finally:
        if streamer:
            streamer.stop()
            active_streams.pop(uid, None)
