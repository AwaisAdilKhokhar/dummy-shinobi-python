from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db, SessionLocal
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.services.camera_service import CameraService
from app.services.motion_detection import MotionDetectionService
from app.services.recording_service import RecordingService
from app.api.auth import get_current_user
from app.models.user import User
from app.models.camera import Camera
from app.models.recording import RecordingType, Recording
from app.models.event import Event, EventType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cameras", tags=["Cameras"])


def motion_detected_callback(camera_id: int, detected_regions: list):
    """Callback when motion is detected - starts recording."""
    db = SessionLocal()
    try:
        # Get camera
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera or not camera.motion_detection_enabled:
            return

        # Check if already recording
        active_recordings = [r for r in RecordingService.active_recordings.keys()]
        camera_recordings = [
            r for r in active_recordings
            if db.query(Recording).filter(Recording.id == r).first() and
               db.query(Recording).filter(Recording.id == r).first().camera_id == camera_id
        ]

        if not camera_recordings:
            # Start recording (60 second clips)
            recording = RecordingService.start_recording(
                db, camera, RecordingType.MOTION, duration=60
            )

            # Log event
            event = Event(
                camera_id=camera_id,
                recording_id=recording.id,
                user_id=camera.owner_id,
                event_type=EventType.MOTION_DETECTED,
                title="Motion Detected",
                description=f"Motion detected in {len(detected_regions)} regions",
                event_data={"regions": detected_regions}
            )
            db.add(event)
            db.commit()

            logger.info(f"Motion detected on camera {camera_id}, started recording {recording.id}")
    except Exception as e:
        logger.error(f"Error in motion detection callback: {e}")
    finally:
        db.close()


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new camera."""
    db_camera = CameraService.create_camera(db, camera, current_user)

    # Start motion detection if enabled
    if db_camera.motion_detection_enabled:
        try:
            MotionDetectionService.start_detection(
                db_camera.id,
                db_camera.stream_url,
                db_camera.motion_sensitivity,
                callback=lambda cam_id, regions: motion_detected_callback(cam_id, regions),
                regions=db_camera.motion_regions
            )
            logger.info(f"Started motion detection for camera {db_camera.id}")
        except Exception as e:
            logger.error(f"Failed to start motion detection for camera {db_camera.id}: {e}")

    return db_camera


@router.get("", response_model=List[CameraResponse])
def get_cameras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all cameras for current user."""
    return CameraService.get_user_cameras(db, current_user, skip, limit)


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific camera."""
    return CameraService.get_camera(db, camera_id, current_user)


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera_update: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a camera."""
    return CameraService.update_camera(db, camera_id, camera_update, current_user)


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a camera."""
    # Stop motion detection if active
    MotionDetectionService.stop_detection(camera_id)
    CameraService.delete_camera(db, camera_id, current_user)
    return None


@router.post("/{camera_id}/motion-detection/toggle")
def toggle_motion_detection(
    camera_id: int,
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle motion detection on/off for a camera."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    camera.motion_detection_enabled = enabled
    db.commit()

    if enabled:
        # Start detection
        try:
            MotionDetectionService.start_detection(
                camera.id,
                camera.stream_url,
                camera.motion_sensitivity,
                callback=lambda cam_id, regions: motion_detected_callback(cam_id, regions),
                regions=camera.motion_regions
            )
            logger.info(f"Motion detection enabled for camera {camera_id}")
            return {"message": "Motion detection enabled", "enabled": True}
        except Exception as e:
            logger.error(f"Failed to start motion detection: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start motion detection: {str(e)}")
    else:
        # Stop detection
        MotionDetectionService.stop_detection(camera.id)
        logger.info(f"Motion detection disabled for camera {camera_id}")
        return {"message": "Motion detection disabled", "enabled": False}


@router.get("/{camera_id}/motion-detection/status")
def get_motion_detection_status(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get motion detection status for a camera."""
    camera = CameraService.get_camera(db, camera_id, current_user)
    is_active = MotionDetectionService.is_detection_active(camera_id)

    return {
        "enabled": camera.motion_detection_enabled,
        "active": is_active,
        "sensitivity": camera.motion_sensitivity
    }
