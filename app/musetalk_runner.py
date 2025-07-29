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
from fal_client.client import FalClientError

try:
    from fal_client import realtime
except Exception:  # fallback if realtime submodule missing
    realtime = None


def run_musetalk(audio_path: str, source_media_path: str, output_path: str,

                 on_update: Optional[Callable] = None) -> None:
    """Generate a talking-head video using the fal.ai MuseTalk API.

    Parameters
    ----------
    audio_path: str
        Local path to the narration audio.
    source_media_path: str
        Path to the avatar image or source video whose lips will be synced.

    output_path: str
        Where to save the resulting video file.
    on_update: Optional[Callable]
        Optional callback for queue updates produced by ``fal_client``.
    """

    # Validate input files
    if not os.path.exists(audio_path):
        raise RuntimeError(f"Audio file not found: {audio_path}")
    if not os.path.exists(source_media_path):
        raise RuntimeError(f"Source media file not found: {source_media_path}")
    
    print(f"Input validation passed:")
    print(f"  Audio file: {audio_path} ({os.path.getsize(audio_path)} bytes)")
    print(f"  Source media: {source_media_path} ({os.path.getsize(source_media_path)} bytes)")

    # Upload input files to fal's temporary storage
    if not os.environ.get("FAL_KEY"):
        raise RuntimeError("FAL_KEY environment variable not set")

    print(f"Uploading audio file: {audio_path}")
    audio_url = fal_client.upload_file(audio_path)
    print(f"Audio uploaded to: {audio_url}")
    
    print(f"Uploading media file: {source_media_path}")
    media_url = fal_client.upload_file(source_media_path)
    print(f"Media uploaded to: {media_url}")

    ext = os.path.splitext(source_media_path)[1].lower()
    # Handle cases where extension might be empty or missing
    if not ext:
        # Check if the file exists and try to determine type from content
        if os.path.exists(source_media_path):
            # Default to video if no extension found
            ext = ".mp4"
            print(f"Warning: No extension found for {source_media_path}, defaulting to .mp4")
    
    media_key = "source_image_url" if ext in {".jpg", ".jpeg", ".png"} else "source_video_url"
    
    print(f"Debug: source_media_path={source_media_path}, ext={ext}, media_key={media_key}")

    # Ensure we're passing the correct parameters to the API
    # MuseTalk API requires both source_video_url and source_image_url fields
    # Use empty string instead of None to avoid validation errors
    api_arguments = {
        "audio_url": audio_url,
        "source_video_url": media_url if media_key == "source_video_url" else "",
        "source_image_url": media_url if media_key == "source_image_url" else ""
    }
    
    print(f"Debug: API arguments={api_arguments}")

    try:
        print(f"Calling fal.ai MuseTalk API with arguments: {api_arguments}")
        print("Starting API call... This may take several minutes for video processing.")
        
        # Add a progress callback if none provided
        def default_progress_update(update):
            print(f"API Progress: {update}")
        
        progress_callback = on_update or default_progress_update
        
        result = fal_client.subscribe(
            "fal-ai/musetalk",
            arguments=api_arguments,
            with_logs=True,  # Always enable logs for debugging
            on_queue_update=progress_callback,
        )
        print(f"API call successful, result keys: {list(result.keys()) if result else 'None'}")
        print(f"Full result: {result}")
        
        # Check if result is None or empty
        if not result:
            raise RuntimeError("API returned empty result")
            
    except FalClientError as exc:
        print(f"FalClientError details: {exc}")
        print(f"FalClientError type: {type(exc)}")
        # Try to get more details about the error
        if hasattr(exc, 'response'):
            print(f"Error response: {exc.response}")
        if hasattr(exc, 'status_code'):
            print(f"Error status code: {exc.status_code}")
        raise RuntimeError(f"MuseTalk API error: {exc}") from exc
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        print(f"Error type: {type(exc)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise RuntimeError(f"Unexpected error calling MuseTalk API: {exc}") from exc


    # Download the produced video
    print("Processing API response...")
    print(f"Result type: {type(result)}")
    print(f"Result content: {result}")
    
    # Handle different possible response formats
    video_info = None
    if isinstance(result, dict):
        video_info = result.get("video")
    elif hasattr(result, 'get'):
        video_info = result.get("video")
    else:
        print(f"Unexpected result type: {type(result)}")
        raise RuntimeError(f"Unexpected result type from API: {type(result)}")
    
    if not video_info:
        print(f"No video info in result. Full result: {result}")
        print(f"Available keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        raise RuntimeError("No video information in API response")
    
    if "url" not in video_info:
        print(f"No URL in video info. Video info: {video_info}")
        print(f"Video info keys: {list(video_info.keys()) if isinstance(video_info, dict) else 'Not a dict'}")
        raise RuntimeError("No video URL in API response")

    print(f"Downloading video from: {video_info['url']}")
    try:
        resp = requests.get(video_info["url"], timeout=120)  # Increased timeout
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to download video: {e}")
        raise RuntimeError(f"Failed to download video: {e}")

    print(f"Downloaded {len(resp.content)} bytes")
    if len(resp.content) == 0:
        raise RuntimeError("Downloaded video is empty")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"Video saved to: {output_path}")


async def stream_musetalk(audio_path: str, source_media_path: str, output_path: Optional[str] = None):

    """Stream MuseTalk frames via fal.ai realtime API.

    Yields base64-encoded JPEG frames as strings. Falls back to regular
    generation if realtime is unavailable.
    """
    if realtime is None:
        # Realtime not supported; run normal inference and yield the result once
        tmp = output_path or os.path.join(os.path.dirname(audio_path), "_tmp.mp4")
        run_musetalk(audio_path, source_media_path, tmp)
        yield f"RESULT::{os.path.basename(tmp)}"
        return

    print(f"Uploading audio file (stream): {audio_path}")
    audio_url = fal_client.upload_file(audio_path)
    print(f"Audio uploaded to (stream): {audio_url}")
    
    print(f"Uploading media file (stream): {source_media_path}")
    media_url = fal_client.upload_file(source_media_path)
    print(f"Media uploaded to (stream): {media_url}")

    ext = os.path.splitext(source_media_path)[1].lower()
    # Handle cases where extension might be empty or missing
    if not ext:
        # Check if the file exists and try to determine type from content
        if os.path.exists(source_media_path):
            # Default to video if no extension found
            ext = ".mp4"
            print(f"Warning (stream): No extension found for {source_media_path}, defaulting to .mp4")
    
    media_key = "source_image_url" if ext in {".jpg", ".jpeg", ".png"} else "source_video_url"
    
    print(f"Debug (stream): source_media_path={source_media_path}, ext={ext}, media_key={media_key}")

    # Ensure we're passing the correct parameters to the API
    # MuseTalk API requires both source_video_url and source_image_url fields
    # Use empty string instead of None to avoid validation errors
    api_arguments = {
        "audio_url": audio_url,
        "source_video_url": media_url if media_key == "source_video_url" else "",
        "source_image_url": media_url if media_key == "source_image_url" else ""
    }
    
    print(f"Debug (stream): API arguments={api_arguments}")

    session = await realtime.connect(
        "fal-ai/musetalk",
        arguments=api_arguments,
    )

    async for event in session:
        frame = event.get("frame") if isinstance(event, dict) else None
        if frame:
            yield frame
    await session.aclose()

