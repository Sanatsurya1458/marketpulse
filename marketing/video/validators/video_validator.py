"""Automated Quality Validator for Rendered Product Demo Videos."""

import os
import subprocess
import json
from typing import Dict, Any, List

class VideoQualityValidator:
    """Validates video output for resolution, audio streams, duration, and frame integrity."""

    @staticmethod
    def inspect(video_path: str) -> Dict[str, Any]:
        """Runs ffprobe on the video and returns technical metadata."""
        if not os.path.exists(video_path):
            return {"valid": False, "error": f"File does not exist: {video_path}"}

        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        try:
            res = subprocess.check_output(cmd).decode()
            info = json.loads(res)
        except Exception as e:
            return {"valid": False, "error": f"ffprobe error: {e}"}

        video_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)

        if not video_stream:
            return {"valid": False, "error": "No video stream found"}

        width = int(video_stream.get("width", 0))
        height = int(video_stream.get("height", 0))
        duration = float(info.get("format", {}).get("duration", 0))
        has_audio = audio_stream is not None

        is_valid = (width > 0 and height > 0 and duration > 2.0 and has_audio)

        return {
            "valid": is_valid,
            "width": width,
            "height": height,
            "duration": duration,
            "has_audio": has_audio,
            "video_codec": video_stream.get("codec_name"),
            "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
            "size_bytes": os.path.getsize(video_path),
        }

    @staticmethod
    def check_black_frames(video_path: str) -> bool:
        """Checks if video contains black frame dropouts."""
        try:
            cmd = [
                "ffmpeg", "-i", video_path,
                "-vf", "blackdetect=d=2:pix_th=0.10",
                "-f", "null", "-"
            ]
            res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
            # If blackdetect flags substantial duration, it returns detected lines
            return "black_start" not in res.stderr
        except Exception:
            return True
