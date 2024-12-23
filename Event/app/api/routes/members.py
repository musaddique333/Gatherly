from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models import EventMemberCreate, EventMemberOut
from app.crud import add_event_member, remove_event_member, get_event_members, get_member_events
from app.utils import validate_user

router = APIRouter()

# Add a member to an event (only if the user is the organizer)
@router.post("/", response_model=EventMemberOut)
def add_member_to_event(member: EventMemberCreate, organizer_email: str, db: Session = Depends(get_db)):
    try:
        validate_user(member.user_email)
    except HTTPException as e:
        raise e
    
    db_member = add_event_member(db=db, event_id=member.event_id, user_email=member.user_email, organizer_email=organizer_email)
    return db_member

# Remove a member from an event (only if the user is the organizer)
@router.delete("/", response_model=EventMemberOut)
def remove_member_from_event(event_id: int, user_email: str, organizer_email: str, db: Session = Depends(get_db)):
    db_member = remove_event_member(db=db, event_id=event_id, user_email=user_email, organizer_email=organizer_email)
    return db_member

# Get members of an event (no restriction, any user can see members if they have access)
@router.get("/{event_id}/members", response_model=List[EventMemberOut])
def get_event_members_route(event_id: int, user_email: str, db: Session = Depends(get_db)):
    return get_event_members(db=db, event_id=event_id, user_email=user_email)