from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.event import EventType


class EventResponse(BaseModel):
    id: int
    camera_id: Optional[int] = None
    recording_id: Optional[int] = None
    user_id: Optional[int] = None
    event_type: EventType
    title: str
    description: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
