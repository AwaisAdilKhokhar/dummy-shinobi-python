from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class EventType(str, enum.Enum):
    MOTION_DETECTED = "motion_detected"
    OBJECT_DETECTED = "object_detected"
    CAMERA_ONLINE = "camera_online"
    CAMERA_OFFLINE = "camera_offline"
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"
    STORAGE_WARNING = "storage_warning"
    ERROR = "error"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Event details
    event_type = Column(SQLEnum(EventType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)

    # Event data
    event_data = Column(JSON)  # Additional event-specific data

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    camera = relationship("Camera", back_populates="events")
    recording = relationship("Recording", back_populates="events")
    user = relationship("User", back_populates="events")
