from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models import ReminderCreate, ReminderOut, EventReminderOut
from app.tasks import send_event_reminder_email
from app.core.db import get_db
from app.crud import get_event, create_reminder_entry, get_reminders, delete_reminder_entry
from app.utils import validate_user

router = APIRouter()

@router.post("/", response_model=ReminderOut)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    """
    Creates a new reminder for an event, ensuring the reminder time is in the future and the event exists.
    
    Arguments:
    - reminder: ReminderCreate containing the event ID, user email, and reminder time.
    - db: Database session dependency.
    
    Returns:
    - A ReminderOut object with the reminder details.
    
    Raises:
    - HTTPException: If the user is invalid, the event doesn't exist, or the reminder time is not in the future.
    """
    try:
        # Validate user email
        validate_user(reminder.user_email)
    except HTTPException as e:
        raise e  # Raise the exception if validation fails

    # Validate that the event exists
    event = get_event(db, reminder.event_id, reminder.user_email)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Validate that the reminder time is in the future
    now = datetime.now(timezone.utc)
    reminder_time = reminder.reminder_time.astimezone(timezone.utc)
    if reminder_time <= now:
        raise HTTPException(status_code=400, detail="Reminder time must be in the future")

    # Create a new reminder entry in the database
    new_reminder = create_reminder_entry(db, reminder)

    # Schedule the reminder email task
    send_event_reminder_email.apply_async(
        args=[new_reminder.reminder_time.isoformat(), new_reminder.user_email, new_reminder.event_id]
    )

    return ReminderOut(
        id=new_reminder.id,
        event_id=new_reminder.event_id,
        user_email=new_reminder.user_email,
        reminder_time=new_reminder.reminder_time
    )

@router.get("/", response_model=list[EventReminderOut])
def read_reminders(user_email: str, db: Session = Depends(get_db)):
    """
    Retrieves a list of events with reminders for a specific user.
    
    Arguments:
    - user_email: The user's email to retrieve reminders for
    - db: Database session dependency
    """
    return get_reminders(db=db, user_email=user_email)

@router.delete("/{reminder_id}", response_model=ReminderOut)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """
    Deletes a reminder by its ID.
    """
    try:
        reminder = delete_reminder_entry(db=db, reminder_id=reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return reminder
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
