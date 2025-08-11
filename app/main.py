from fastapi import (
    FastAPI,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Form,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import asyncio
import shutil
import json
import subprocess

import openai
import requests
from gtts import gTTS
from pydantic import BaseModel
# Import the runner in a way that works for both ``uvicorn app.main:app`` and
# ``streamlit run app/main.py`` execution modes.
try:  # package style
    from app.musetalk_runner import run_musetalk, stream_musetalk  # type: ignore
except Exception:
    # Script execution -- ensure this file's directory is on ``sys.path``
    import sys
    from pathlib import Path


    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from musetalk_runner import run_musetalk, stream_musetalk  # type: ignore

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


# Prepare a default class from bundled input assets
DEFAULT_ID = "default"


def _prepare_default_class() -> None:
    """Copy demo assets into place and pre-generate the default avatar."""

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    src_dir = "inputs"
    src_audio = os.path.join(src_dir, "audio.wav")
    src_ts = os.path.join(src_dir, "timestamps.json")
    src_avatar = os.path.join(src_dir, "avatar1.mp4")
    src_slides_id = os.path.join(src_dir, "slides_id.txt")
    dst_audio = os.path.join("uploads", f"{DEFAULT_ID}_audio.wav")
    dst_ts = os.path.join("uploads", f"{DEFAULT_ID}_timestamps.json")
    dst_avatar = os.path.join("uploads", f"{DEFAULT_ID}_avatar.mp4")
    dst_slides_id = os.path.join("uploads", f"{DEFAULT_ID}_slides_id.txt")

    try:
        shutil.copyfile(src_audio, dst_audio)
        shutil.copyfile(src_ts, dst_ts)
        shutil.copyfile(src_avatar, dst_avatar)
        shutil.copyfile(src_slides_id, dst_slides_id)
    except FileNotFoundError:
        # If any demo asset is missing, simply skip generation
        return

    # Generate slide images for the default class. First attempt to extract
    # frames from the bundled demo video; if that fails, fall back to
    # placeholder images so that slide navigation still works.
    src_video = os.path.join(src_dir, "video.mp4")
    generated = False
    try:
        with open(dst_ts) as f:
            times = json.load(f)
        if os.path.exists(src_video):
            for i, t in enumerate(times[:-1]):
                img_path = os.path.join("uploads", f"{DEFAULT_ID}_slide_{i+1}.png")
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    str(t),
                    "-i",
                    src_video,
                    "-vframes",
                    "1",
                    img_path,
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            generated = True
    except Exception as exc:
        print(f"Failed to extract slides from video: {exc}")

    if not generated:
        try:
            with open(dst_ts) as f:
                times = json.load(f)
            for i in range(len(times) - 1):
                url = f"https://placehold.co/1280x720?text=Slide+{i+1}"
                img_path = os.path.join("uploads", f"{DEFAULT_ID}_slide_{i+1}.png")
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.ok:
                        with open(img_path, "wb") as imgf:
                            imgf.write(resp.content)
                except Exception:
                    break
        except Exception:
            pass

    output_path = os.path.join("outputs", f"{DEFAULT_ID}.mp4")
    if not os.path.exists(output_path):
        try:
            run_musetalk(dst_audio, dst_avatar, output_path)
        except Exception as exc:  # best-effort
            print(f"Failed to generate default class: {exc}")


_prepare_default_class()

@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/upload")
def upload_page():
    return FileResponse("static/upload.html")

@app.post("/upload")
async def upload(
    audio: UploadFile,
    timestamps: UploadFile,
    avatar: UploadFile,
    slides_id: str = Form(...),
):
    uid = uuid.uuid4().hex
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Save all uploaded files
    paths = {
        "audio": os.path.join("uploads", f"{uid}_audio.wav"),
        "timestamps": os.path.join("uploads", f"{uid}_timestamps.json"),
        "avatar": os.path.join("uploads", f"{uid}_avatar{os.path.splitext(avatar.filename)[1] or '.mp4'}"),
    }
    for file, path in zip([audio, timestamps, avatar], paths.values()):
        with open(path, "wb") as f:
            f.write(await file.read())

    # Save slides presentation id
    with open(os.path.join("uploads", f"{uid}_slides_id.txt"), "w") as f:
        f.write(slides_id.strip())

    # Generate avatar video in a thread so the event loop is not blocked
    output_path = os.path.join("outputs", f"{uid}.mp4")
    try:
        await asyncio.to_thread(
            run_musetalk, paths["audio"], paths["avatar"], output_path
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


    return {
        "id": uid,
        "output_video": f"{uid}.mp4",
        "timestamps": os.path.basename(paths["timestamps"]),
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

    output_path = os.path.join("outputs", f"{uid}_stream.mp4")
    streamer = stream_musetalk(audio_path, avatar_path, output_path)


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


class ChatRequest(BaseModel):
    uid: str
    question: str
    slide_index: int
    slide_text: str | None = None


@app.post("/chat")
async def chat(req: ChatRequest):
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])


    prompt = f"You are helping a student. They are currently on slide {req.slide_index}. Slide text: {req.slide_text or ''}. Question: {req.question}"

    try:
        completion = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        answer = completion.choices[0].message.content.strip()

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    try:
        tts = gTTS(answer)
        audio_path = os.path.join("uploads", f"{req.uid}_qa.mp3")
        tts.save(audio_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TTS error: {exc}")

    avatar_path = None
    for ext in [".mp4", ".jpg", ".png"]:
        p = os.path.join("uploads", f"{req.uid}_avatar{ext}")
        if os.path.exists(p):
            avatar_path = p
            break
    if not avatar_path:
        raise HTTPException(status_code=404, detail="Avatar not found")

    output_name = f"{req.uid}_qa_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join("outputs", output_name)
    try:
        await asyncio.to_thread(run_musetalk, audio_path, avatar_path, output_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MuseTalk error: {exc}")

    return {"answer": answer, "video": output_name}
