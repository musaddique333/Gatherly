from sqlalchemy.orm import Session
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
        organizer_id=event.organizer_id,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
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
    db.delete(db_event)
    db.commit()
    return db_event

# Add a member to an event
def add_event_member(db: Session, event_id: int, user_email: str):
    # Check if the event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

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