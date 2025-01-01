from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models import EventOut, EventCreate, EventUpdate
from app.crud import create_event, get_events, get_event, update_event, delete_event
from app.core.db import get_db
from app.utils import validate_user
from app.tasks import send_event_created_email

router = APIRouter()

# Create a new event
@router.post("/", response_model=EventOut)
def create_new_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Creates a new event in the system.
    
    Validates the organizer's email and adds the event to the database.
    After event creation, sends a notification email to the organizer.
    """
    try:
        # Validate organizer's email through an authentication microservice
        validate_user(event.organizer_email)
    except HTTPException as e:
        raise e  # Raise the exception if validation fails

    created_event = create_event(db=db, event=event)

    # Send email notification about the event creation
    send_event_created_email.apply_async((created_event.id, event.organizer_email))
    
    return created_event

# Get all events that the user is a member of
@router.get("/", response_model=List[EventOut])
def read_events(user_email: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieves a list of events where the user is a member.
    
    Arguments:
    - user_email: The user's email to check membership
    - skip: Number of events to skip (pagination)
    - limit: Maximum number of events to return (pagination)
    """
    return get_events(db=db, user_email=user_email, skip=skip, limit=limit)

# Get a single event by its ID (only if the user is a member)
@router.get("/{event_id}", response_model=EventOut)
def read_event(event_id: str, user_email: str, db: Session = Depends(get_db)):
    """
    Retrieves a single event by its ID if the user is a member of the event.
    
    Arguments:
    - event_id: The ID of the event to retrieve
    - user_email: The user's email to check membership
    """
    return get_event(db=db, event_id=event_id, user_email=user_email)

# Update an existing event by its ID (only if the user is the organizer)
@router.put("/{event_id}", response_model=EventOut)
def update_existing_event(event_id: str, event: EventUpdate, user_email: str, db: Session = Depends(get_db)):
    """
    Updates an existing event by its ID, only if the user is the event organizer.
    
    Arguments:
    - event_id: The ID of the event to update
    - event: The updated event data
    - user_email: The user's email to verify if they are the organizer
    """
    return update_event(db=db, event_id=event_id, event=event, user_email=user_email)

# Delete an event by its ID (only by organizer)
@router.delete("/{event_id}", response_model=EventOut)
def delete_existing_event(event_id: str, user_email: str, db: Session = Depends(get_db)):
    """
    Deletes an event by its ID, only if the user is the event organizer.
    
    Arguments:
    - event_id: The ID of the event to delete
    - user_email: The user's email to verify if they are the organizer
    """
    deleted_event = delete_event(db=db, event_id=event_id, user_email=user_email)
    return deleted_event