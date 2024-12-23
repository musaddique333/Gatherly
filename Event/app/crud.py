from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import EventMember, Event, EventCreate, EventUpdate

# Create a new event
def create_event(db: Session, event: EventCreate):
    db_event = Event(
        title=event.title,
        date=event.date,
        description=event.description,
        location=event.location,
        num_members=event.num_members,
        tags=event.tags,
        is_online=event.is_online,
        organizer_email=event.organizer_email,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Add the organizer as a member of the event
    event_member = EventMember(event_id=db_event.id, user_email=event.organizer_email)
    db.add(event_member)
    db.commit()

    return db_event

# Get all events
def get_events(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Event).offset(skip).limit(limit).all()

# Get a single event by ID
def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

# Update an event
def update_event(db: Session, event_id: int, event: EventUpdate):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

# Delete an event
def delete_event(db: Session, event_id: int):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    
    # Delete all associated event members
    db.query(EventMember).filter(EventMember.event_id == event_id).delete()

    db.delete(db_event)
    db.commit()
    return db_event

def add_event_member(db: Session, event_id: int, user_email: str):
    # Check if the event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    # Check if the member already exists for the event
    existing_member = (
        db.query(EventMember)
        .filter(EventMember.event_id == event_id, EventMember.user_email == user_email)
        .first()
    )

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_email} is already a member of event {event_id}"
        )
    # Create and add the member
    event_member = EventMember(event_id=event_id, user_email=user_email)
    db.add(event_member)
    db.commit()
    db.refresh(event_member)
    return event_member


# Remove a member from an event
def remove_event_member(db: Session, event_id: int, user_email: str):
    event_member = (
        db.query(EventMember)
        .filter(EventMember.event_id == event_id, EventMember.user_email == user_email)
        .first()
    )
    if not event_member:
        return None

    db.delete(event_member)
    db.commit()
    return event_member

# Get members of an event
def get_event_members(db: Session, event_id: int):
    return db.query(EventMember).filter(EventMember.event_id == event_id).all()

# Get all event of user
def get_member_events(db: Session, user_email: str):
    return db.query(EventMember).filter(EventMember.user_email == user_email).all()