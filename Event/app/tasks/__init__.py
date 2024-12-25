from app.core.celery_config import celery_app
from app.models import EventMember, Event, Reminder
from app.utils import send_email  # Import the email sending function
from datetime import datetime, timedelta
from app.core.db import SessionLocal

# Task to send event creation email to the organizer
@celery_app.task
def send_event_created_email(event_id: int, organizer_email: str):
    # Use SessionLocal to query the Event table
    with SessionLocal() as db:
        event = db.query(Event).get(event_id)
        if event:
            send_email(
                subject="Event Created",
                recipient=organizer_email,
                body=f"Your event '{event.title}' has been created successfully!"
            )
        else:
            # Handle case where event is not found
            print(f"Event with id {event_id} not found.")

# Task to send email to the new member when added to an event
@celery_app.task
def send_member_added_email(event_id: int, member_email: str):
    with SessionLocal() as db:
        event = db.query(Event).get(event_id)
        if event:
            send_email(
                subject="Added to Event",
                recipient=member_email,
                body=f"You have been added to the event '{event.title}'"
            )
        else:
            print(f"Event with id {event_id} not found.")

# Task to send event reminder emails to members
@celery_app.task
def send_event_reminder_email(reminder_time: str, member_email: str, event_id: int):
    # Convert the reminder time to datetime
    reminder_time = datetime.fromisoformat(reminder_time)
    with SessionLocal() as db:
        event = db.query(Event).get(event_id)
        if event:
            send_email(
                subject="Event Reminder",
                recipient=member_email,
                body=f"Reminder: The event '{event.title}' set for {reminder_time}"
            )
        else:
            print(f"Event with id {event_id} not found.")

# Task to send event reminder emails to members
@celery_app.task
def send_reminder():
    with SessionLocal() as db:
        try:
            current_time = datetime.now()
            reminders = db.query(Reminder).filter(Reminder.reminder_time <= current_time).all()
            for reminder in reminders:
                subject = "Event Reminder"
                body = f"Hello, {reminder.user_email}! This is a reminder for the event '{reminder.event.title}', happening soon."
                send_email(reminder.user_email, subject, body)
        finally:
            db.close()
