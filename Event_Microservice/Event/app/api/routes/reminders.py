from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models import ReminderCreate, ReminderOut
from app.tasks import send_event_reminder_email
from app.core.db import get_db
from app.crud import get_event, create_reminder_entry
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
