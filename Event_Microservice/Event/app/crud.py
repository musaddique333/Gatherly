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

# Get all events for a user (that they are a member of)
def get_events(db: Session, user_email: str, skip: int = 0, limit: int = 10):
    return db.query(Event).join(EventMember).filter(EventMember.user_email == user_email).offset(skip).limit(limit).all()

# Get a single event by its ID (only if the user is a member)
def get_event(db: Session, event_id: int, user_email: str):
    # Check if the event exists and if the user is a member of the event
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with ID {event_id} not found"
        )

    # Ensure the user is part of the event
    is_member = db.query(EventMember).filter(EventMember.event_id == event_id, EventMember.user_email == user_email).first()
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User is not a member of this event"
        )
    
    return db_event

# Update an event (only if the user is the organizer)
def update_event(db: Session, event_id: int, event: EventUpdate, user_email: str):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with ID {event_id} not found"
        )

    # Ensure only the organizer can update the event
    if db_event.organizer_email != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the organizer can update this event"
        )

    # Update the event with the provided data
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

# Delete an event (only if the user is the organizer)
def delete_event(db: Session, event_id: int, user_email: str):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with ID {event_id} not found"
        )

    # Ensure only the organizer can delete the event
    if db_event.organizer_email != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the organizer can delete this event"
        )

    # Delete all associated event members
    db.query(EventMember).filter(EventMember.event_id == event_id).delete()

    db.delete(db_event)
    db.commit()
    return db_event

# Add a member to an event, ensuring the user is the organizer
def add_event_member(db: Session, event_id: int, user_email: str, organizer_email: str):
    # Check if the event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with ID {event_id} not found"
        )

    # Ensure the user is the organizer before adding a member
    if event.organizer_email != organizer_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only the organizer can add members to this event"
        )

    # Check if the member already exists for the event
    existing_member = db.query(EventMember).filter(EventMember.event_id == event_id, EventMember.user_email == user_email).first()
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

# Remove a member from an event, ensuring the user is the organizer
def remove_event_member(db: Session, event_id: int, user_email: str, organizer_email: str):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with ID {event_id} not found"
        )

    # Ensure only the organizer can remove members
    if event.organizer_email != organizer_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only the organizer can remove members from this event"
        )

    # Prevent the organizer from removing themselves
    if event.organizer_email == user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Organizer cannot remove themselves from the event"
        )

    # Find the event member
    event_member = db.query(EventMember).filter(EventMember.event_id == event_id, EventMember.user_email == user_email).first()
    if not event_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Member not found"
        )

    db.delete(event_member)
    db.commit()
    return event_member

# Get members of an event
def get_event_members(db: Session, event_id: int, user_email: str):
    # Check if the event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    # Check if the user is a member of the event
    user_member = db.query(EventMember).filter(
        EventMember.event_id == event_id,
        EventMember.user_email == user_email
    ).first()

    if not user_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this event"
        )

    # Retrieve and return the members
    return db.query(EventMember).filter(EventMember.event_id == event_id).all()