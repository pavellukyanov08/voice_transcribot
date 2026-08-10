import subprocess
import tempfile
import os
from pathlib import Path


def extract_audio_from_video(video_path: str) -> str:
    suffix = ".mp3"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.close()

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-ar", "16000",
            "-ac", "1",
            "-b:a", "64k",
            tmp.name,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        os.unlink(tmp.name)
        raise RuntimeError(f"ffmpeg error: {result.stderr}")

    return tmp.name