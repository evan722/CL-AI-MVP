import asyncio
import base64
import subprocess
import os
from asyncio import Queue

class MuseTalkStreamer:
    def __init__(self, audio_path, face_img):
        self.audio = audio_path
        self.face = face_img
        self.queue = Queue()
        self.proc = None

    async def start(self):
        # Change to musetalk directory for proper module imports
        original_cwd = os.getcwd()
        
        # Handle both Docker (/app) and local environments
        if '/app' in original_cwd:
            # In Docker, the structure is /app/...
            musetalk_dir = '/app/musetalk'
            workspace_dir = '/app'
        else:
            # Local development environment
            musetalk_dir = os.path.join(original_cwd, "musetalk")
            workspace_dir = original_cwd
        
        # Set PYTHONPATH to include the workspace root
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{workspace_dir}:{env.get('PYTHONPATH', '')}"
        
        cmd = [
            "python3", "-m", "musetalk.scripts.realtime_inference",
            "--inference_config", "configs/inference/realtime.yaml",
            "--audio_clips", os.path.join(workspace_dir, self.audio),
            "--avatar_id", "0"
        ]
        self.proc = await asyncio.create_subprocess_exec(
            *cmd, 
            stdout=subprocess.PIPE, 
            cwd=musetalk_dir,
            env=env
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
    # Change to musetalk directory and run inference script directly
    original_cwd = os.getcwd()
    
    # Handle both Docker (/app) and local environments
    if '/app' in original_cwd:
        # In Docker, the structure is /app/...
        musetalk_dir = '/app/musetalk'
        workspace_dir = '/app'
    else:
        # Local development environment
        musetalk_dir = os.path.join(original_cwd, "musetalk")
        workspace_dir = original_cwd
    
    try:
        # Set PYTHONPATH to include the workspace root
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{workspace_dir}:{env.get('PYTHONPATH', '')}"
        
        cmd = [
            "python3", "-m", "musetalk.scripts.inference",
            "--pose_style", "0",
            "--audio_path", os.path.join(workspace_dir, audio_path),
            "--output_path", os.path.join(workspace_dir, output_path),
            "--input_image", os.path.join(workspace_dir, face_img),
            "--still", "True",
            "--batch_size", "2"
        ]
        subprocess.run(cmd, check=True, cwd=musetalk_dir, env=env)
    finally:
        pass
