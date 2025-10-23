from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import logging

from app.database import get_db
from app.schemas.recording import RecordingResponse
from app.services.camera_service import CameraService
from app.services.recording_service import RecordingService
from app.api.auth import get_current_user
from app.models.user import User
from app.models.recording import RecordingType, Recording

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recordings", tags=["Recordings"])


@router.post("/{camera_id}/start")
def start_recording(
    camera_id: int,
    recording_type: RecordingType = RecordingType.MANUAL,
    duration: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start recording from a camera."""
    camera = CameraService.get_camera(db, camera_id, current_user)
    recording = RecordingService.start_recording(db, camera, recording_type, duration)
    return {"message": "Recording started", "recording_id": recording.id}


@router.post("/{recording_id}/stop")
def stop_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop an active recording."""
    logger.info(f"Stop recording request for recording {recording_id}")
    RecordingService.stop_recording(db, recording_id)
    return {"message": "Recording stopped"}


@router.get("/debug/active")
def get_active_recordings(
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check active recordings."""
    active_recording_ids = list(RecordingService.active_recordings.keys())
    logger.info(f"Active recordings: {active_recording_ids}")
    return {
        "active_recording_ids": active_recording_ids,
        "count": len(active_recording_ids)
    }


@router.get("/camera/{camera_id}", response_model=List[RecordingResponse])
def get_camera_recordings(
    camera_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recordings for a camera."""
    # Verify camera ownership
    CameraService.get_camera(db, camera_id, current_user)
    return RecordingService.get_recordings(db, camera_id, skip, limit)


@router.get("/{recording_id}/download")
def download_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a recording file."""
    logger.info(f"Download request for recording {recording_id}")

    # Get recording
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        logger.error(f"Recording {recording_id} not found in database")
        raise HTTPException(status_code=404, detail="Recording not found in database")

    # Verify camera ownership
    CameraService.get_camera(db, recording.camera_id, current_user)

    logger.info(f"Recording file path: {recording.file_path}")
    logger.info(f"Recording file exists: {os.path.exists(recording.file_path)}")
    logger.info(f"Recording file size: {recording.file_size} bytes")
    logger.info(f"Recording duration: {recording.duration} seconds")

    if not os.path.exists(recording.file_path):
        # Check parent directory
        parent_dir = os.path.dirname(recording.file_path)
        logger.error(f"Recording file not found at: {recording.file_path}")
        logger.error(f"Parent directory exists: {os.path.exists(parent_dir)}")
        if os.path.exists(parent_dir):
            logger.error(f"Files in directory: {os.listdir(parent_dir)}")
        raise HTTPException(status_code=404, detail=f"Recording file not found at {recording.file_path}")

    logger.info(f"Serving file: {recording.file_path}")
    return FileResponse(recording.file_path, media_type="video/mp4", filename=os.path.basename(recording.file_path))


@router.get("/{recording_id}/thumbnail")
def get_recording_thumbnail(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recording thumbnail."""
    # Get recording
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Verify camera ownership
    CameraService.get_camera(db, recording.camera_id, current_user)

    if not recording.thumbnail_path or not os.path.exists(recording.thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(recording.thumbnail_path, media_type="image/jpeg")
