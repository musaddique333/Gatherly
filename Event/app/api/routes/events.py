from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import EventOut, EventCreate, EventUpdate
from app.crud import create_event, get_events, get_event, update_event, delete_event
from app.core.db import get_db
from app.utils import validate_user

router = APIRouter()

# Create a new event
@router.post("/", response_model=EventOut)
def create_new_event(event: EventCreate, db: Session = Depends(get_db)):
    # Validate organizer ID from the Authentication microservice
    try:
        validate_user(event.organizer_email)
    except HTTPException as e:
        raise e 
    return create_event(db=db, event=event)

# Get all events
@router.get("/", response_model=List[EventOut])
def read_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_events(db=db, skip=skip, limit=limit)

# Get a single event by ID
@router.get("/{event_id}", response_model=EventOut)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_event = get_event(db=db, event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

# Update an existing event
@router.put("/{event_id}", response_model=EventOut)
def update_existing_event(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    updated_event = update_event(db=db, event_id=event_id, event=event)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

# Delete an event
@router.delete("/{event_id}", response_model=EventOut)
def delete_existing_event(event_id: int, db: Session = Depends(get_db)):
    deleted_event = delete_event(db=db, event_id=event_id)
    if not deleted_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return deleted_event
