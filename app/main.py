from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .replicate_api import generate_avatar

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.post("/generate")
async def generate(text: str = Form(...), audio_url: str = Form(...)):
    try:
        video_url = generate_avatar(text, audio_url)
        return JSONResponse({"video_url": video_url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
