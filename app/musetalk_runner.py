import asyncio
import base64
import subprocess
from asyncio import Queue

class MuseTalkStreamer:
    def __init__(self, audio_path, face_img):
        self.audio = audio_path
        self.face = face_img
        self.queue = Queue()
        self.proc = None

    async def start(self):
        # Use the musetalk package as a module so imports work
        cmd = [
            "python3", "-m", "musetalk.scripts.realtime_inference",
            "--inference_config", "musetalk/configs/inference/realtime.yaml",
            "--audio_clips", self.audio,
            "--avatar_id", "0"
        ]
        self.proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE
        )
        asyncio.create_task(self._read_frames())

    async def _read_frames(self):
        while True:
            try:
                hdr = await self.proc.stdout.readexactly(4)
                length = int.from_bytes(hdr, "big")
                jpg = await self.proc.stdout.readexactly(length)
                self.queue.put_nowait(base64.b64encode(jpg).decode())
            except asyncio.IncompleteReadError:
                break
            except Exception:
                break

    async def next_frame(self):
        return await asyncio.wait_for(self.queue.get(), timeout=0.1)

    def stop(self):
        if self.proc and self.proc.returncode is None:
            self.proc.kill()

def run_musetalk(audio_path, face_img, output_path):
    # Run inference module via -m so that musetalk package is on PYTHONPATH
    cmd = [
        "python3", "-m", "musetalk.scripts.inference",
        "--pose_style", "0",
        "--audio_path", audio_path,
        "--output_path", output_path,
        "--input_image", face_img,
        "--still", "True",
        "--batch_size", "2"
    ]
    subprocess.run(cmd, check=True)
