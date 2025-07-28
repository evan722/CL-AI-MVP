"""Wrapper around the fal.ai MuseTalk API.

The previous codebase executed the MuseTalk model locally which required a
heavy environment and large downloads.  This module replaces that behaviour by
leveraging the hosted model available on `fal.ai`.  The ``run_musetalk``
function uploads the required audio and video files, invokes the remote model
and stores the resulting video in the given ``output_path``.
"""

from typing import Callable, Optional

import os

import requests
import fal_client
try:
    from fal_client import realtime
except Exception:  # fallback if realtime submodule missing
    realtime = None


def run_musetalk(audio_path: str, source_video_path: str, output_path: str,
                 on_update: Optional[Callable] = None) -> None:
    """Generate a talking-head video using the fal.ai MuseTalk API.

    Parameters
    ----------
    audio_path: str
        Local path to the narration audio.
    source_video_path: str
        Local path to the source video whose lips will be synced.
    output_path: str
        Where to save the resulting video file.
    on_update: Optional[Callable]
        Optional callback for queue updates produced by ``fal_client``.
    """

    # Upload input files to fal's temporary storage
    audio_url = fal_client.upload_file(audio_path)
    video_url = fal_client.upload_file(source_video_path)

    result = fal_client.subscribe(
        "fal-ai/musetalk",
        arguments={
            "source_video_url": video_url,
            "audio_url": audio_url,
        },
        with_logs=bool(on_update),
        on_queue_update=on_update,
    )

    # Download the produced video
    video_info = result.get("video")
    if not video_info or "url" not in video_info:
        raise RuntimeError("Invalid response from MuseTalk API")

    resp = requests.get(video_info["url"], timeout=60)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)


async def stream_musetalk(audio_path: str, source_video_path: str):
    """Stream MuseTalk frames via fal.ai realtime API.

    Yields base64-encoded JPEG frames as strings. Falls back to regular
    generation if realtime is unavailable.
    """
    if realtime is None:
        # Realtime not supported; run normal inference and yield the result once
        tmp = os.path.join(os.path.dirname(audio_path), "_tmp.mp4")
        run_musetalk(audio_path, source_video_path, tmp)
        yield f"RESULT::{tmp}"
        return

    audio_url = fal_client.upload_file(audio_path)
    video_url = fal_client.upload_file(source_video_path)

    session = await realtime.connect(
        "fal-ai/musetalk",
        arguments={"source_video_url": video_url, "audio_url": audio_url},
    )

    async for event in session:
        frame = event.get("frame") if isinstance(event, dict) else None
        if frame:
            yield frame
    await session.aclose()

