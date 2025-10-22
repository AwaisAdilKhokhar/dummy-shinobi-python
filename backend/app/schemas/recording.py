from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.recording import RecordingType


class RecordingResponse(BaseModel):
    id: int
    camera_id: int
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    recording_type: RecordingType
    start_time: datetime
    end_time: Optional[datetime] = None
    codec: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    bitrate: Optional[int] = None
    thumbnail_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
