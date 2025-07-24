import asyncio, base64, subprocess
from asyncio import Queue

class MuseTalkStreamer:
    def __init__(self, audio_path, face_img):
        self.audio = audio_path
        self.face = face_img
        self.queue = Queue()
        self.proc = None

    async def start(self):
        cmd = [
            "python3", "musetalk/scripts/realtime_inference.py",
            "--inference_config", "musetalk/configs/inference/realtime.yaml",
            "--audio_clips", self.audio, "--avatar_id", "0"
        ]
        self.proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE)
        asyncio.create_task(self._read_frames())

    async def _read_frames(self):
        while True:
            hdr = await self.proc.stdout.readexactly(4)
            length = int.from_bytes(hdr, "big")
            jpg = await self.proc.stdout.readexactly(length)
            self.queue.put_nowait(base64.b64encode(jpg).decode())

    async def next_frame(self):
        return await asyncio.wait_for(self.queue.get(), timeout=0.1)

    def stop(self):
        if self.proc and self.proc.returncode is None:
            self.proc.kill()
