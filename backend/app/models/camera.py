from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class CameraStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    RECORDING = "recording"


class RecordingMode(str, enum.Enum):
    CONTINUOUS = "continuous"
    MOTION = "motion"
    SCHEDULED = "scheduled"
    DISABLED = "disabled"


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    # Connection details
    stream_url = Column(String, nullable=False)  # RTSP, HTTP, etc.
    protocol = Column(String, default="rtsp")  # rtsp, http, onvif
    username = Column(String)
    password = Column(String)

    # Camera settings
    resolution = Column(String, default="1920x1080")
    fps = Column(Integer, default=15)
    codec = Column(String, default="h264")

    # Recording settings
    recording_mode = Column(SQLEnum(RecordingMode), default=RecordingMode.MOTION)
    recording_quality = Column(Integer, default=80)  # 0-100
    max_recording_days = Column(Integer, default=7)

    # Motion detection
    motion_detection_enabled = Column(Boolean, default=True)
    motion_sensitivity = Column(Integer, default=50)  # 0-100
    motion_regions = Column(JSON)  # Array of regions {x, y, width, height}

    # Status
    status = Column(SQLEnum(CameraStatus), default=CameraStatus.OFFLINE)
    last_seen = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Metadata
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="cameras")
    recordings = relationship("Recording", back_populates="camera", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="camera", cascade="all, delete-orphan")
