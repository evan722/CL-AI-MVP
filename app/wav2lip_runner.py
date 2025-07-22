import subprocess
import os

class Wav2LipStreamer:
    @staticmethod
    def run(video_path, audio_path):
        out_path = "static/avatar.mp4"
        cmd = [
            "python3", "wav2lip/inference.py",
            "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
            "--face", video_path,
            "--audio", audio_path,
            "--outfile", out_path
        ]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd)
