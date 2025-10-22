import subprocess
import os
from typing import Dict, Optional
from app.utils.ffmpeg import FFmpegProcessor
from app.config import get_settings

settings = get_settings()


class StreamService:
    """Video streaming service."""

    active_streams: Dict[int, subprocess.Popen] = {}

    @classmethod
    def start_stream(cls, camera_id: int, stream_url: str, username: Optional[str] = None,
                     password: Optional[str] = None) -> str:
        """Start HLS stream for camera."""
        # Stop existing stream if any
        cls.stop_stream(camera_id)

        # Create stream directory
        stream_dir = os.path.join(settings.STREAM_PATH, str(camera_id))
        os.makedirs(stream_dir, exist_ok=True)

        # Start FFmpeg process
        cmd = FFmpegProcessor.get_hls_stream_cmd(stream_url, stream_dir, username, password)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        cls.active_streams[camera_id] = process

        # Return playlist URL
        return f"/streams/{camera_id}/stream.m3u8"

    @classmethod
    def stop_stream(cls, camera_id: int):
        """Stop HLS stream for camera."""
        if camera_id in cls.active_streams:
            process = cls.active_streams[camera_id]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            del cls.active_streams[camera_id]

    @classmethod
    def is_stream_active(cls, camera_id: int) -> bool:
        """Check if stream is active."""
        if camera_id in cls.active_streams:
            process = cls.active_streams[camera_id]
            return process.poll() is None
        return False

    @classmethod
    def cleanup_inactive_streams(cls):
        """Clean up inactive streams."""
        inactive = []
        for camera_id, process in cls.active_streams.items():
            if process.poll() is not None:
                inactive.append(camera_id)

        for camera_id in inactive:
            del cls.active_streams[camera_id]
