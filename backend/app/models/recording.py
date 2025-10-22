from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class RecordingType(str, enum.Enum):
    CONTINUOUS = "continuous"
    MOTION = "motion"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)

    # Recording details
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger)  # In bytes
    duration = Column(Integer)  # In seconds

    # Recording metadata
    recording_type = Column(SQLEnum(RecordingType), default=RecordingType.CONTINUOUS)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))

    # Video properties
    codec = Column(String)
    resolution = Column(String)
    fps = Column(Integer)
    bitrate = Column(Integer)

    # Thumbnail
    thumbnail_path = Column(String)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    camera = relationship("Camera", back_populates="recordings")
    events = relationship("Event", back_populates="recording")
