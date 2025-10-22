from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.services.camera_service import CameraService
from app.services.stream_service import StreamService
from app.api.auth import get_current_user
from app.models.user import User
from app.config import get_settings

router = APIRouter(prefix="/stream", tags=["Streaming"])
settings = get_settings()


@router.post("/{camera_id}/start")
def start_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start HLS stream for a camera."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    playlist_url = StreamService.start_stream(
        camera.id,
        camera.stream_url,
        camera.username,
        camera.password
    )

    return {"message": "Stream started", "playlist_url": playlist_url}


@router.post("/{camera_id}/stop")
def stop_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop HLS stream for a camera."""
    # Verify camera ownership
    CameraService.get_camera(db, camera_id, current_user)

    StreamService.stop_stream(camera_id)
    return {"message": "Stream stopped"}


@router.get("/{camera_id}/status")
def get_stream_status(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stream status."""
    # Verify camera ownership
    CameraService.get_camera(db, camera_id, current_user)

    is_active = StreamService.is_stream_active(camera_id)
    return {"camera_id": camera_id, "is_active": is_active}


@router.get("/{camera_id}/playlist.m3u8")
def get_playlist(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get HLS playlist."""
    # Verify camera ownership
    CameraService.get_camera(db, camera_id, current_user)

    playlist_path = os.path.join(settings.STREAM_PATH, str(camera_id), "stream.m3u8")

    if not os.path.exists(playlist_path):
        raise HTTPException(status_code=404, detail="Stream not found")

    return FileResponse(playlist_path, media_type="application/vnd.apple.mpegurl")


@router.get("/{camera_id}/{segment_file}")
def get_segment(
    camera_id: int,
    segment_file: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get HLS segment."""
    # Verify camera ownership
    CameraService.get_camera(db, camera_id, current_user)

    segment_path = os.path.join(settings.STREAM_PATH, str(camera_id), segment_file)

    if not os.path.exists(segment_path):
        raise HTTPException(status_code=404, detail="Segment not found")

    return FileResponse(segment_path, media_type="video/mp2t")
