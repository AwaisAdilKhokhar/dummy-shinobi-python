from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from app.models.camera import CameraStatus, RecordingMode


class MotionRegion(BaseModel):
    x: int
    y: int
    width: int
    height: int


class CameraBase(BaseModel):
    name: str
    description: Optional[str] = None
    stream_url: str
    protocol: str = "rtsp"
    username: Optional[str] = None
    password: Optional[str] = None
    resolution: str = "1920x1080"
    fps: int = 15
    codec: str = "h264"


class CameraCreate(CameraBase):
    recording_mode: RecordingMode = RecordingMode.MOTION
    recording_quality: int = 80
    max_recording_days: int = 7
    motion_detection_enabled: bool = True
    motion_sensitivity: int = 50
    motion_regions: Optional[List[MotionRegion]] = None


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stream_url: Optional[str] = None
    protocol: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    codec: Optional[str] = None
    recording_mode: Optional[RecordingMode] = None
    recording_quality: Optional[int] = None
    max_recording_days: Optional[int] = None
    motion_detection_enabled: Optional[bool] = None
    motion_sensitivity: Optional[int] = None
    motion_regions: Optional[List[MotionRegion]] = None
    is_active: Optional[bool] = None


class CameraResponse(CameraBase):
    id: int
    recording_mode: RecordingMode
    recording_quality: int
    max_recording_days: int
    motion_detection_enabled: bool
    motion_sensitivity: int
    motion_regions: Optional[List[Dict]] = None
    status: CameraStatus
    last_seen: Optional[datetime] = None
    is_active: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
