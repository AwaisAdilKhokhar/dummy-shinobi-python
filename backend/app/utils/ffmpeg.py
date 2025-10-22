import subprocess
import os
from typing import Optional, Dict
import json


class FFmpegProcessor:
    """FFmpeg utility for video processing."""

    @staticmethod
    def get_stream_info(stream_url: str, username: Optional[str] = None, password: Optional[str] = None) -> Optional[Dict]:
        """Get stream information using ffprobe."""
        try:
            # Build authentication URL if credentials provided
            if username and password and "rtsp://" in stream_url:
                stream_url = stream_url.replace("rtsp://", f"rtsp://{username}:{password}@")

            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-show_format",
                stream_url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"Error getting stream info: {e}")
            return None

    @staticmethod
    def start_recording(stream_url: str, output_path: str, duration: Optional[int] = None,
                       username: Optional[str] = None, password: Optional[str] = None) -> subprocess.Popen:
        """Start recording from stream."""
        # Build authentication URL if credentials provided
        if username and password and "rtsp://" in stream_url:
            stream_url = stream_url.replace("rtsp://", f"rtsp://{username}:{password}@")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", stream_url,
            "-c", "copy",
            "-f", "mp4",
            "-movflags", "+faststart"
        ]

        if duration:
            cmd.extend(["-t", str(duration)])

        cmd.append(output_path)

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process

    @staticmethod
    def generate_thumbnail(video_path: str, output_path: str, timestamp: str = "00:00:01") -> bool:
        """Generate thumbnail from video."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", timestamp,
                "-vframes", "1",
                "-q:v", "2",
                output_path,
                "-y"
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return False

    @staticmethod
    def get_hls_stream_cmd(stream_url: str, output_dir: str, username: Optional[str] = None,
                          password: Optional[str] = None) -> list:
        """Get FFmpeg command for HLS streaming."""
        # Build authentication URL if credentials provided
        if username and password and "rtsp://" in stream_url:
            stream_url = stream_url.replace("rtsp://", f"rtsp://{username}:{password}@")

        os.makedirs(output_dir, exist_ok=True)
        playlist_path = os.path.join(output_dir, "stream.m3u8")

        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", stream_url,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-c:a", "aac",
            "-f", "hls",
            "-hls_time", "2",
            "-hls_list_size", "5",
            "-hls_flags", "delete_segments",
            playlist_path
        ]

        return cmd
