from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.db import get_db
from app.models import EventMemberCreate, EventMemberOut
from app.crud import add_event_member, remove_event_member, get_event_members
from app.utils import validate_user
from app.tasks import send_member_added_email

router = APIRouter()

# Add a member to an event (only if the user is the organizer)
@router.post("/", response_model=EventMemberOut)
def add_member_to_event(member: EventMemberCreate, organizer_email: str, db: Session = Depends(get_db)):
    """
    Adds a member to an event, but only if the user is the event organizer.
    
    Arguments:
    - member: EventMemberCreate containing the event ID and user email
    - organizer_email: The email of the event organizer
    - db: Database session dependency
    
    Returns:
    - The added event member
    """
    try:
        # Validate the user before adding to the event
        validate_user(member.user_email)
    except HTTPException as e:
        raise e  # Raise the exception if validation fails

    # Add the member to the event
    db_member = add_event_member(db=db, event_id=member.event_id, user_email=member.user_email, organizer_email=organizer_email)

    # Send email notification about the member being added
    send_member_added_email.apply_async((member.event_id, member.user_email))
    
    return db_member

# Remove a member from an event (only if the user is the organizer)
@router.delete("/", response_model=EventMemberOut)
def remove_member_from_event(event_id: UUID, user_email: str, organizer_email: str, db: Session = Depends(get_db)):
    """
    Removes a member from an event, but only if the user is the event organizer.
    
    Arguments:
    - event_id: The ID of the event
    - user_email: The email of the member to be removed
    - organizer_email: The email of the event organizer
    - db: Database session dependency
    
    Returns:
    - The removed event member
    """
    db_member = remove_event_member(db=db, event_id=event_id, user_email=user_email, organizer_email=organizer_email)
    return db_member

# Get members of an event (no restriction, any user can see members if they have access)
@router.get("/{event_id}/members", response_model=List[EventMemberOut])
def get_event_members_route(event_id: UUID, user_email: str, db: Session = Depends(get_db)):
    """
    Retrieves the members of a specific event.
    
    Arguments:
    - event_id: The ID of the event
    - user_email: The user's email to check access
    - db: Database session dependency
    
    Returns:
    - A list of event members
    """
    return get_event_members(db=db, event_id=event_id, user_email=user_email)