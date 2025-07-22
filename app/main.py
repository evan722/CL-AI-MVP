import os, uuid, aiofiles, json, asyncio, subprocess, tempfile, base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketState
from .wav2lip_runner import Wav2LipStreamer

ROOT = Path(__file__).parent.parent
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True, parents=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return (ROOT / "static" / "index.html").read_text()

# -------- upload endpoint -------------------------------------------------
@app.post("/upload")
async def upload(
    video: UploadFile,
    audio: UploadFile,
    times: UploadFile,           # timestamps.json
):
    uid = uuid.uuid4().hex
    vpath = UPLOADS / f"{uid}_video.mp4"
    apath = UPLOADS / f"{uid}_audio.wav"
    tpath = UPLOADS / f"{uid}_timestamps.json"

    # save files
    async with aiofiles.open(vpath, "wb") as f:
        while chunk := await video.read(1 << 20):
            await f.write(chunk)
    async with aiofiles.open(apath, "wb") as f:
        while chunk := await audio.read(1 << 20):
            await f.write(chunk)
    async with aiofiles.open(tpath, "wb") as f:
        data = await times.read()
        await f.write(data)

    return {"id": uid}

# -------- websocket for avatar frames ------------------------------------
active_streams: dict[str, Wav2LipStreamer] = {}

@app.websocket("/ws/avatar/{uid}")
async def avatar_ws(ws: WebSocket, uid: str):
    await ws.accept()
    streamer = None
    try:
        # initialise on connect
        audio_file = UPLOADS / f"{uid}_audio.wav"
        streamer = Wav2LipStreamer(str(audio_file))
        active_streams[uid] = streamer
        asyncio.create_task(streamer.run())

        while True:
            if ws.application_state != WebSocketState.CONNECTED:
                break
            # push next frame if playing
            if streamer.play.is_set():
                frame = await streamer.next_frame()
                if frame:
                    await ws.send_text(frame)
            # receive commands
            if ws.client_state == WebSocketState.DISCONNECTED:
                break
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
                pass
    except WebSocketDisconnect:
        pass
    finally:
        if streamer:
            streamer.stop()
            active_streams.pop(uid, None)
