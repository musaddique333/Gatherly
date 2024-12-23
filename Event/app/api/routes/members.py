from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models import EventMemberCreate, EventMemberOut
from app.crud import add_event_member, remove_event_member, get_event_members, get_member_events
from app.utils import validate_user

router = APIRouter()

# Add a member to an event
@router.post("/", response_model=EventMemberOut)
def add_member_to_event(member: EventMemberCreate, db: Session = Depends(get_db)):
    try:
        validate_user(member.user_email)
    except HTTPException as e:
        raise e
    
    db_member = add_event_member(db=db, event_id=member.event_id, user_email=member.user_email)
    if not db_member:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_member

# Remove a member from an event
@router.delete("/", response_model=EventMemberOut)
def remove_member_from_event(event_id: int, user_email: str, db: Session = Depends(get_db)):
    db_member = remove_event_member(db=db, event_id=event_id, user_email=user_email)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

# Get members of an event
@router.get("/{event_id}/members", response_model=List[EventMemberOut])
def get_event_members_route(event_id: int, db: Session = Depends(get_db)):
    return get_event_members(db=db, event_id=event_id)

# # Get events of a member
# @router.get("/{event_id}/members", response_model=List[EventMemberOut])
# def get_member_events_route(user_email: str, db: Session = Depends(get_db)):
#     return get_member_events(db=db, user_email=user_email)