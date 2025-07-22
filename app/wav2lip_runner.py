import asyncio
import base64
from asyncio import Queue, Event
from typing import Optional


class Wav2LipStreamer:
    """
    Wrapper that:
    1. Launches `wav2lip/inference.py` as a subprocess.
    2. Reads JPEG frames as raw bytes from stdout, base64-encodes them,
       and feeds them to an async queue.
    3. Supports play/pause and (naïve) seek by restarting the process.
    """

    def __init__(self, audio_path: str):
        self.audio_path: str = audio_path
        self.face_img: str = "static/avatar_face.jpg"
        self.weights: str = "wav2lip/checkpoints/wav2lip_gan.pth"
        self.proc: Optional[asyncio.subprocess.Process] = None
        self.queue: Queue[str] = Queue(maxsize=2)
        self.play: Event = Event()
        self.play.set()  # Start in playing state

    # ------------------------------------------------------------------
    async def run(self):
        """Start Wav2Lip subprocess and stream frames into the queue."""
        cmd = [
            "python3", "wav2lip/inference.py",
            "--checkpoint_path", self.weights,
            "--face", self.face_img,
            "--audio", self.audio_path,
            "--outfile", "-",  # Output to stdout
            "--fps", "25"
        ]

        try:
            self.proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                bufsize=0
            )

            while True:
                hdr = await self.proc.stdout.readexactly(4)
                frame_len = int.from_bytes(hdr, "big")
                jpg = await self.proc.stdout.readexactly(frame_len)
                b64 = base64.b64encode(jpg).decode()

                await self.play.wait()
                await self.queue.put(b64)

        except asyncio.IncompleteReadError:
            pass  # Process ended
        except Exception as e:
            print(f"[Wav2LipStreamer] Error during run: {e}")
        finally:
            await self.stop()

    # ------------------------------------------------------------------
    async def next_frame(self) -> Optional[str]:
        """Return next base64 frame (or None if queue is empty)."""
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=0.1)
        except asyncio.TimeoutError:
            return None

    # ------------------------------------------------------------------
    async def seek(self, _t: float):
        """Restart the subprocess from the beginning (naïve seek)."""
        await self.stop()
        self.queue = Queue(maxsize=2)
        asyncio.create_task(self.run())

    # ------------------------------------------------------------------
    async def stop(self):
        """Stop the subprocess safely."""
        if self.proc and self.proc.returncode is None:
            try:
                self.proc.kill()
                await asyncio.wait_for(self.proc.wait(), timeout=1)
            except asyncio.TimeoutError:
                self.proc.terminate()
            finally:
                self.proc = None
