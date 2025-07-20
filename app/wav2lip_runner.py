import subprocess, asyncio, base64, tempfile, os, json, wave
from asyncio import Event
from pathlib import Path

WEIGHTS = "wav2lip/checkpoints/wav2lip_gan.pth"
FACE_IMG = "static/avatar_face.jpg"  # replace with your teacher portrait

class Wav2LipStreamer:
    def __init__(self, audio_file: str):
        self.audio_file = audio_file
        self.play = Event(); self.play.set()
        self.proc = None
        self._stdout_task = None
        self._buf = asyncio.Queue()

    async def run(self):
        """Launch Wav2Lip subprocess that writes raw JPEG frames to stdout."""
         cmd = [
             "python", "wav2lip/inference.py",
             "--face", FACE_IMG,
             "--audio", self.audio_file,
             "--outfile", "-",  # pipe output
             "--checkpoint_path", "wav2lip/checkpoints/wav2lip_gan.pth"
            ]

        self.proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE
        )
        self._stdout_task = asyncio.create_task(self._reader())

    async def _reader(self):
        while True:
            if self.proc.stdout.at_eof():
                break
            # each frame is sent as length-prefixed bytes: <4‑byte int><jpg bytes>
            size_bytes = await self.proc.stdout.readexactly(4)
            size = int.from_bytes(size_bytes, "big")
            jpg = await self.proc.stdout.readexactly(size)
            await self._buf.put(base64.b64encode(jpg).decode())

    async def next_frame(self):
        if not self.play.is_set():  # paused
            await asyncio.sleep(0.033)
            return ""
        try:
            return await asyncio.wait_for(self._buf.get(), timeout=0.05)
        except asyncio.TimeoutError:
            return ""

    def seek(self, t: float):
        # naïve: restart at new timestamp
        self.stop()
        self.__init__(self.audio_file)
        asyncio.create_task(self.run())

    def stop(self):
        self.proc and self.proc.kill()
