from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.event import EventResponse
from app.models.event import Event, EventType
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=List[EventResponse])
def get_events(
    camera_id: Optional[int] = None,
    event_type: Optional[EventType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get events for current user."""
    query = db.query(Event).filter(Event.user_id == current_user.id)

    if camera_id:
        query = query.filter(Event.camera_id == camera_id)

    if event_type:
        query = query.filter(Event.event_type == event_type)

    events = query.order_by(Event.created_at.desc()).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific event."""
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
