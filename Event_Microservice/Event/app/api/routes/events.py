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

# Get all events that the user is a member of
@router.get("/", response_model=List[EventOut])
def read_events(user_email: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_events(db=db, user_email=user_email, skip=skip, limit=limit)

# Get a single event by its ID (only if the user is a member)
@router.get("/{event_id}", response_model=EventOut)
def read_event(event_id: int, user_email: str, db: Session = Depends(get_db)):
    return get_event(db=db, event_id=event_id, user_email=user_email)

# Update an existing event by its ID (only if the user is the organizer)
@router.put("/{event_id}", response_model=EventOut)
def update_existing_event(event_id: int, event: EventUpdate, user_email: str, db: Session = Depends(get_db)):
    return update_event(db=db, event_id=event_id, event=event, user_email=user_email)

# Delete an event by its ID
# Delete an event by its ID (only by organizer)
@router.delete("/{event_id}", response_model=EventOut)
def delete_existing_event(event_id: int, user_email: str, db: Session = Depends(get_db)):
    deleted_event = delete_event(db=db, event_id=event_id, user_email=user_email)
    return deleted_event