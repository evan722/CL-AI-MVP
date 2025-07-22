import asyncio
import base64
import subprocess
from pathlib import Path
from asyncio import Queue, Event


class Wav2LipStreamer:
    """
    Very‑light wrapper that:
    1. Launches `wav2lip/inference.py` as a subprocess.
    2. Reads JPEG frames as raw bytes from stdout, base64‑encodes, and
       feeds them to an async queue.
    3. Supports play/pause and (naïve) seek by restarting the process.
    """

    def __init__(self, audio_path: str):
        self.audio_path = audio_path
        self.face_img = "static/avatar_face.jpg"
        self.weights = "wav2lip/checkpoints/wav2lip_gan.pth"
        self.proc: subprocess.Popen | None = None
        self.queue: Queue[str] = Queue(maxsize=2)
        self.play: Event = Event()
        self.play.set()          # start in “playing” state

    # ------------------------------------------------------------------
    async def run(self):
        """Start Wav2Lip and continuously read frames into the queue."""
        cmd = [
            "python3", "wav2lip/inference.py",
            "--checkpoint_path", self.weights,
            "--face", self.face_img,
            "--audio", self.audio_path,
            "--outfile", "-",          # stream frames to stdout
            "--fps", "25"
        ]

        # Launch subprocess
        self.proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )

        # Continuously read length‑prefixed JPEG frames from stdout
        try:
            while True:
                hdr = await self.proc.stdout.readexactly(4)
                frame_len = int.from_bytes(hdr, "big")
                jpg = await self.proc.stdout.readexactly(frame_len)
                b64 = base64.b64encode(jpg).decode()

                await self.play.wait()
                await self.queue.put(b64)
        except asyncio.IncompleteReadError:
            pass
        finally:
            self.stop()

    # ------------------------------------------------------------------
    async def next_frame(self) -> str | None:
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=0.1)
        except asyncio.TimeoutError:
            return None

    # ------------------------------------------------------------------
    def seek(self, _t: float):
        self.stop()
        self.queue = Queue(maxsize=2)
        asyncio.create_task(self.run())

    # ------------------------------------------------------------------
    def stop(self):
        if self.proc and self.proc.returncode is None:
            self.proc.kill()
            try:
                self.proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
