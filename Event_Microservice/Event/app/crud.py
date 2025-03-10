from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone
from app.utils import validate_user

from app.models import EventMember, Event, EventCreate, EventUpdate, Reminder, ReminderCreate, EventOut

# fet user name from grpc
def get_username(email: str):
    try:
        # Validate organizer's email through an authentication microservice
        return validate_user(email)["username"]
    except HTTPException as e:
        raise e  # Raise the exception if validation fails

# Create a new event
def create_event(db: Session, event: EventCreate):
    """
    Create a new event and add the organizer as a member.

    Args:
        db (Session): The database session.
        event (EventCreate): The event details to be created.

    Returns:
        Event: The created event object.
    
    Raises:
        HTTPException: If there is an error creating the event.
    """
    try:
        db_event = Event(
            title=event.title,
            date=event.date,
            description=event.description,
            location=event.location,
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

        username = get_username(db_event.organizer_email)
        event_out = EventOut(**db_event.to_dict(), username=username)
        return event_out
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating event: {str(e)}")

# Get all events for a user (that they are a member of)
def get_all_events(db: Session):
    """
    Get a list of events that a user is a member of.

    Args:
        db (Session): The database session.
    Returns:
        List[Event]: List of all events currently active.
    """
    try:
        events = db.query(Event).all()
        event_list_with_username = []

        for event in events:
            username = get_username(event.organizer_email) 
            # Create a new EventOutWithUsername object
            event_with_username = EventOut(
                **event.to_dict(),
                username=username
            )
            event_list_with_username.append(event_with_username)

        return event_list_with_username
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving events: {str(e)}")

# Get all events for a user (that they are a member of)
def get_events(db: Session, user_email: str):
    """
    Get a list of events that a user is a member of.

    Args:
        db (Session): The database session.
        user_email (str): The user's email to check membership.

    Returns:
        List[Event]: List of events the user is a member of.
    """
    try:
        events = db.query(Event).join(EventMember).filter(EventMember.user_email == user_email).all()
        event_list_with_username = []

        for event in events:
            username = get_username(event.organizer_email) 
            # Create a new EventOutWithUsername object
            event_with_username = EventOut(
                **event.to_dict(),
                username=username
            )
            event_list_with_username.append(event_with_username)

        return event_list_with_username
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving events: {str(e)}")

# Get a single event by its ID (only if the user is a member)
def get_event(db: Session, event_id: UUID, user_email: str):
    """
    Get a single event by its ID, ensuring the user is a member.

    Args:
        db (Session): The database session.
        event_id (UUID): The event's ID.
        user_email (str): The user's email to verify membership.

    Returns:
        dict: A dictionary containing event data (or empty event if not a member).
    """
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with ID {event_id} not found"
        )

    # Ensure the user is part of the event
    is_member = db.query(EventMember).filter(EventMember.event_id == event_id, EventMember.user_email == user_email).first()
    if not is_member:
        # Send the access request to join the event
        from app.tasks import send_join_request
        send_join_request.apply_async(
            args=[user_email, db_event.organizer_email, event_id]
        )

        # Return a response with an empty EventOut and a message
        empty_event = EventOut(
            title="", 
            date=datetime.now(timezone.utc), 
            description="", 
            location="", 
            tags=[], 
            is_online=False, 
            id="ebb1543d-21c2-4ddb-af81-dcea218c8213",
            organizer_email=user_email,
            username=""
        )
        return empty_event
    
    username = get_username(db_event.organizer_email)
    event_out = EventOut(**db_event.to_dict(), username=username)
    return event_out


# Update an event (only if the user is the organizer)
def update_event(db: Session, event_id: UUID, event: EventUpdate, user_email: str):
    """
    Update an existing event, ensuring only the organizer can perform this action.

    Args:
        db (Session): The database session.
        event_id (UUID): The event's ID to update.
        event (EventUpdate): The new event data.
        user_email (str): The user's email to verify if they are the organizer.

    Returns:
        Event: The updated event object.

    Raises:
        HTTPException: If the event doesn't exist or the user is not the organizer.
    """
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
    username = get_username(db_event.organizer_email)
    event_out = EventOut(**db_event.to_dict(), username=username)
    return event_out

# Delete an event (only if the user is the organizer)
def delete_event(db: Session, event_id: UUID, user_email: str):
    """
    Delete an event and remove all associated members, ensuring only the organizer can delete it.

    Args:
        db (Session): The database session.
        event_id (UUID): The event's ID to delete.
        user_email (str): The user's email to verify if they are the organizer.

    Returns:
        Event: The deleted event object.

    Raises:
        HTTPException: If the event doesn't exist or the user is not the organizer.
    """
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
    username = get_username(db_event.organizer_email)
    event_out = EventOut(**db_event.to_dict(), username=username)
    try:
        # Delete all associated event members
        db.query(EventMember).filter(EventMember.event_id == event_id).delete()

        db.delete(db_event)
        db.commit()
        return event_out
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting event: {str(e)}")

# Add a member to an event, ensuring the user is the organizer
def add_event_member(db: Session, event_id: UUID, user_email: str, organizer_email: str):
    """
    Add a new member to an event if the user is the organizer and the user is not already a member.

    Args:
        db (Session): The database session.
        event_id (UUID): The event's ID.
        user_email (str): The email of the user to add.
        organizer_email (str): The email of the organizer.

    Returns:
        EventMember: The newly added event member.

    Raises:
        HTTPException: If the event does not exist, the user is not the organizer, or the user is already a member.
    """
    try:
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error adding member: {str(e)}")


# Remove a member from an event, ensuring the user is the organizer
def remove_event_member(db: Session, event_id: UUID, user_email: str, organizer_email: str):
    """
    Remove a member from an event if the user is the organizer, ensuring the organizer cannot remove themselves.

    Args:
        db (Session): The database session.
        event_id (UUID): The event's ID.
        user_email (str): The email of the user to remove.
        organizer_email (str): The email of the organizer.

    Returns:
        EventMember: The removed event member.

    Raises:
        HTTPException: If the event does not exist, the user is not the organizer, or the user is not a member.
    """
    try:
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error removing member: {str(e)}")


# Get members of an event
def get_event_members(db: Session, event_id: UUID, user_email: str):
    """
    Retrieve all members of an event, ensuring the user is a member.

    Args:
        db (Session): The database session.
        event_id (UUID): The event's ID.
        user_email (str): The user's email to verify membership.

    Returns:
        List[EventMember]: The list of event members.

    Raises:
        HTTPException: If the event does not exist or the user is not a member.
    """
    try:
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving members: {str(e)}")


def create_reminder_entry(db: Session, reminder: ReminderCreate):
    """
    Create a new reminder entry for an event.

    Args:
        db (Session): The database session.
        reminder (ReminderCreate): The reminder data.

    Returns:
        Reminder: The newly created reminder object.

    Raises:
        HTTPException: If there is an error creating the reminder.
    """
    try:
        new_reminder = Reminder(
            event_id=reminder.event_id,
            user_email=reminder.user_email,
            reminder_time=reminder.reminder_time
        )
        db.add(new_reminder)
        db.commit()
        db.refresh(new_reminder)
        return new_reminder
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating reminder: {str(e)}")

def delete_reminder_entry(db: Session, reminder_id: int):
    """
    Delete a reminder entry by its ID.

    Args:
        db (Session): The database session.
        reminder_id (int): The ID of the reminder to be deleted.

    Returns:
        bool: True if deletion is successful, False if reminder not found.

    Raises:
        HTTPException: If there is an error deleting the reminder.
    """
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if reminder:
            db.delete(reminder)
            db.commit()
            return reminder
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting reminder: {str(e)}")
    
def get_reminders(db: Session, user_email: str):
    """
    Retrieve a list of events with reminders for a specific user.

    Args:
        db (Session): The database session.
        user_email (str): The user's email to retrieve reminders for.

    Returns:
        List[EventReminderOut]: A list of events with reminders for the user.
    """
    try:
        return (
            db.query(Event)
            .join(EventMember)
            .join(Reminder)
            .filter(EventMember.user_email == user_email)
            .with_entities(
                Event.id.label("event_id"),
                Event.title,
                Event.date,
                Event.description,
                Event.location,
                Event.tags,
                Event.is_online,
                Event.organizer_email,
                Reminder.reminder_time,
                Reminder.id.label("reminder_id")
            )
            .all()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving reminders: {str(e)}",
        )