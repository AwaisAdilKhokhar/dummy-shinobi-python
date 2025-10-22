from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.camera import Camera, CameraStatus
from app.models.user import User
from app.schemas.camera import CameraCreate, CameraUpdate
from app.utils.ffmpeg import FFmpegProcessor
from datetime import datetime


class CameraService:
    """Camera management service."""

    @staticmethod
    def create_camera(db: Session, camera: CameraCreate, user: User) -> Camera:
        """Create a new camera."""
        # Verify stream is accessible
        stream_info = FFmpegProcessor.get_stream_info(
            camera.stream_url,
            camera.username,
            camera.password
        )

        # Create camera even if stream check fails (might be temporarily unavailable)
        db_camera = Camera(
            name=camera.name,
            description=camera.description,
            stream_url=camera.stream_url,
            protocol=camera.protocol,
            username=camera.username,
            password=camera.password,
            resolution=camera.resolution,
            fps=camera.fps,
            codec=camera.codec,
            recording_mode=camera.recording_mode,
            recording_quality=camera.recording_quality,
            max_recording_days=camera.max_recording_days,
            motion_detection_enabled=camera.motion_detection_enabled,
            motion_sensitivity=camera.motion_sensitivity,
            motion_regions=[region.dict() for region in camera.motion_regions] if camera.motion_regions else None,
            status=CameraStatus.ONLINE if stream_info else CameraStatus.OFFLINE,
            owner_id=user.id
        )

        db.add(db_camera)
        db.commit()
        db.refresh(db_camera)
        return db_camera

    @staticmethod
    def get_camera(db: Session, camera_id: int, user: User) -> Camera:
        """Get camera by ID."""
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camera not found"
            )

        # Check ownership
        if camera.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this camera"
            )

        return camera

    @staticmethod
    def get_user_cameras(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Camera]:
        """Get all cameras for a user."""
        return db.query(Camera).filter(Camera.owner_id == user.id).offset(skip).limit(limit).all()

    @staticmethod
    def update_camera(db: Session, camera_id: int, camera_update: CameraUpdate, user: User) -> Camera:
        """Update camera."""
        camera = CameraService.get_camera(db, camera_id, user)

        update_data = camera_update.dict(exclude_unset=True)

        # Convert motion_regions if present
        if "motion_regions" in update_data and update_data["motion_regions"]:
            update_data["motion_regions"] = [region.dict() for region in update_data["motion_regions"]]

        for field, value in update_data.items():
            setattr(camera, field, value)

        db.commit()
        db.refresh(camera)
        return camera

    @staticmethod
    def delete_camera(db: Session, camera_id: int, user: User):
        """Delete camera."""
        camera = CameraService.get_camera(db, camera_id, user)
        db.delete(camera)
        db.commit()

    @staticmethod
    def update_camera_status(db: Session, camera_id: int, status: CameraStatus):
        """Update camera status."""
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if camera:
            camera.status = status
            camera.last_seen = datetime.utcnow()
            db.commit()
