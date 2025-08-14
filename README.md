# MuseTalk API App

This project shows how to integrate the [fal.ai](https://fal.ai) hosted
**MuseTalk** model into a FastAPI web application. Users upload:

* a **slides PDF** *or* Google Slides presentation ID
* the matching **audio narration**
* a **timestamps.json** file for slide cues
* an **avatar image or video** (JPG/PNG or MP4)

The server forwards the audio and avatar to the remote API and returns a
talking-head video.  The slides video and timestamps are used on the
frontend to synchronise playback.  A WebSocket endpoint provides a
real‑time preview if the model supports it.

## Running locally

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Obtain an API key from [fal.ai](https://fal.ai) and set it as ``FAL_KEY``:
   ```bash
   export FAL_KEY=YOUR_API_KEY
   ```
3. Start the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

4. Visit `http://localhost:8080` to access the web interface. A demo lesson
   from the `inputs/` folder loads automatically. Use the **Upload Class**
   page to provide your own assets (slides PDF or Google Slides ID, audio,
   timestamps and avatar).

All heavy computation happens on fal.ai.  No local models are required,
but the ``FAL_KEY`` environment variable must be present.

## GPT Chat Feature

The application now includes an optional chatbot that answers questions about
the current slide. To enable it, obtain an OpenAI API key and set
``OPENAI_API_KEY`` before starting the server:

```bash
export OPENAI_API_KEY=your_openai_key
```

While playing the lesson, pause and type a question in the textbox. The backend
will query GPT, synthesise audio using ``gTTS`` and generate a short video of
the avatar speaking the answer. After playback finishes, the lesson resumes
automatically.

## Default demo content

The `inputs/` folder contains `slides.pdf`, `audio.wav`, `timestamps.json` and
`avatar1.mp4`. These are copied into place at startup so the home page always
shows a working example. Replace these files with your own before launching the
server to change the preloaded class.


## New Next.js Frontend

A modern React UI is available in the `frontend/` directory. It wraps the existing upload and player flows without changing any API routes. See `frontend/README.md` for setup and integration instructions.
