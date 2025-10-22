from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.recording import Recording, RecordingType
from app.models.camera import Camera
from app.utils.ffmpeg import FFmpegProcessor
from app.config import get_settings
import os
import subprocess

settings = get_settings()


class RecordingService:
    """Recording management service."""

    active_recordings: dict = {}

    @classmethod
    def start_recording(cls, db: Session, camera: Camera, recording_type: RecordingType = RecordingType.CONTINUOUS,
                       duration: Optional[int] = None) -> Recording:
        """Start recording from camera."""
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"camera_{camera.id}_{timestamp}.mp4"
        file_path = os.path.join(settings.RECORDINGS_PATH, str(camera.id), filename)

        # Create recording record
        recording = Recording(
            camera_id=camera.id,
            file_path=file_path,
            recording_type=recording_type,
            start_time=datetime.utcnow(),
            codec=camera.codec,
            resolution=camera.resolution,
            fps=camera.fps
        )
        db.add(recording)
        db.commit()
        db.refresh(recording)

        # Start FFmpeg process
        process = FFmpegProcessor.start_recording(
            camera.stream_url,
            file_path,
            duration,
            camera.username,
            camera.password
        )

        cls.active_recordings[recording.id] = process

        return recording

    @classmethod
    def stop_recording(cls, db: Session, recording_id: int):
        """Stop active recording."""
        if recording_id in cls.active_recordings:
            process = cls.active_recordings[recording_id]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            del cls.active_recordings[recording_id]

            # Update recording record
            recording = db.query(Recording).filter(Recording.id == recording_id).first()
            if recording:
                recording.end_time = datetime.utcnow()
                if os.path.exists(recording.file_path):
                    recording.file_size = os.path.getsize(recording.file_path)
                    recording.duration = int((recording.end_time - recording.start_time).total_seconds())

                    # Generate thumbnail
                    thumbnail_path = recording.file_path.replace('.mp4', '_thumb.jpg')
                    if FFmpegProcessor.generate_thumbnail(recording.file_path, thumbnail_path):
                        recording.thumbnail_path = thumbnail_path

                db.commit()

    @classmethod
    def get_recordings(cls, db: Session, camera_id: int, skip: int = 0, limit: int = 100) -> List[Recording]:
        """Get recordings for a camera."""
        return db.query(Recording).filter(
            Recording.camera_id == camera_id
        ).order_by(Recording.start_time.desc()).offset(skip).limit(limit).all()

    @classmethod
    def delete_old_recordings(cls, db: Session, camera: Camera):
        """Delete old recordings based on retention policy."""
        cutoff_date = datetime.utcnow() - timedelta(days=camera.max_recording_days)

        old_recordings = db.query(Recording).filter(
            Recording.camera_id == camera.id,
            Recording.start_time < cutoff_date
        ).all()

        for recording in old_recordings:
            # Delete files
            if os.path.exists(recording.file_path):
                os.remove(recording.file_path)
            if recording.thumbnail_path and os.path.exists(recording.thumbnail_path):
                os.remove(recording.thumbnail_path)

            # Delete record
            db.delete(recording)

        db.commit()
