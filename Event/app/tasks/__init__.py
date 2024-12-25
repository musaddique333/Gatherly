from app.core.celery_config import celery_app
from app.models import Event, Reminder
from app.utils import send_email
from datetime import datetime, timezone, timedelta
from app.core.db import SessionLocal
from app.crud import delete_reminder_entry

import logging

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Task to send event creation email to the organizer
@celery_app.task
def send_event_created_email(event_id: int, organizer_email: str):
    """
    Send an email to the event organizer confirming the event creation.

    Args:
        event_id (int): The ID of the created event.
        organizer_email (str): The email address of the event organizer.
    """
    try:
        with SessionLocal() as db:
            event = db.query(Event).get(event_id)
            if event:
                # Prepare HTML and Plaintext bodies
                html_body=f"""
                <html>
                <body>
                    <h2 style="color: #333;">Event Creation Successful!</h2>
                    <p>Hello,</p>
                    <p>Congratulations! Your event titled <strong>{event.title}</strong> has been successfully created and is now live. Below are the details for your reference:</p>
                    <ul>
                        <li><strong>Event Title:</strong> {event.title}</li>
                        <li><strong>Date & Time:</strong> {event.date.strftime('%Y-%m-%d at %H:%M:%S')}</li>
                        <li><strong>Description:</strong> {event.description or 'No description provided.'}</li>
                        <li><strong>Location:</strong> {event.location or 'Not specified'}</li>
                        <li><strong style="color: red;">Room ID:{event.id}</strong></li>
                    </ul>
                    <p>Thank you for using our platform, and we wish you all the best in organizing your event!</p>
                    <br>
                    <p><strong>Best regards,</strong></p>
                    <p>The Event Team</p>
                </body>
                </html>
                """

                plain_body=f"""
                Event Creation Successful!

                Hello,

                Congratulations! Your event titled "{event.title}" has been successfully created and is now live. Below are the details for your reference:

                Event Title: {event.title}
                Date & Time: {event.date.strftime('%Y-%m-%d at %H:%M:%S')}
                Description: {event.description or 'No description provided.'}
                Location: {event.location or 'Not specified'}
                Room ID: {event.id}

                Thank you for using our platform, and we wish you all the best in organizing your event!

                Best regards,
                The Event Team
                """

                # Send email with both HTML and plaintext content
                send_email(
                    subject=f"Your Event '{event.title}' Has Been Successfully Created!",
                    recipient=organizer_email,
                    plain_body=plain_body,
                    html_body=html_body 
                )

                logger.info(f"Event creation email sent to {organizer_email} for event {event_id}.")
            else:
                logger.error(f"Event with id {event_id} not found.")
    except Exception as e:
        logger.error(f"Error in send_event_created_email task: {str(e)}")



# Task to send email to the new member when added to an event
@celery_app.task
def send_member_added_email(event_id: int, member_email: str):
    """
    Send an email to a new member when added to an event.

    Args:
        event_id (int): The ID of the event the member was added to.
        member_email (str): The email address of the new member.
    """
    try:
        with SessionLocal() as db:
            event = db.query(Event).get(event_id)
            if event:
                # Prepare HTML and Plaintext bodies
                html_body = f"""
                <html>
                <body>
                    <h2 style="color: #333;">You’ve Been Added to an Event!</h2>
                    <p>Hi {member_email},</p>
                    <p>We are excited to inform you that you have been successfully added to the event <strong>"{event.title}"</strong>. Here are the details:</p>
                    <ul>
                        <li><strong>Event Title:</strong> {event.title}</li>
                        <li><strong>Date & Time:</strong> {event.date.strftime('%Y-%m-%d at %H:%M:%S')}</li>
                        <li><strong>Description:</strong> {event.description or 'No description provided.'}</li>
                        <li><strong>Location:</strong> {event.location or 'Not specified'}</li>
                        <li><strong style="color: red;">Room ID: {event.id}</strong></li>
                    </ul>
                    <p>Please mark your calendar and feel free to reach out if you have any questions.</p>
                    <br>
                    <p><strong>Best regards,</strong></p>
                    <p>The Event Team</p>
                </body>
                </html>
                """

                plaintext_body = f"""
                You’ve Been Added to an Event!

                Hi {member_email},

                We are excited to inform you that you have been successfully added to the event "{event.title}". Here are the details:

                Event Title: {event.title}
                Date & Time: {event.date.strftime('%Y-%m-%d at %H:%M:%S')}
                Description: {event.description or 'No description provided.'}
                Location: {event.location or 'Not specified'}
                Room ID: {event.id}

                Please mark your calendar and feel free to reach out if you have any questions.

                Best regards,
                The Event Team
                """

                # Send email with both HTML and plaintext content
                send_email(
                    subject=f"You’ve Been Added to an Event '{event.title}'!",
                    recipient=member_email,
                    plain_body=plaintext_body,
                    html_body=html_body 
                )

                logger.info(f"Member added email sent to {member_email} for event {event_id}.")
            else:
                logger.error(f"Event with id {event_id} not found.")
    except Exception as e:
        logger.error(f"Error in send_member_added_email task: {str(e)}")



# Task to send event reminder emails to members
@celery_app.task
def send_event_reminder_email(reminder_time: str, member_email: str, event_id: int):
    """
    Send a reminder email to a member for an event.

    Args:
        reminder_time (str): The time of the reminder in ISO format.
        member_email (str): The email address of the member to send the reminder.
        event_id (int): The ID of the event for the reminder.
    """
    try:
        reminder_time = datetime.fromisoformat(reminder_time)
        with SessionLocal() as db:
            event = db.query(Event).get(event_id)
            if event:
                # Prepare HTML and Plaintext bodies
                html_body = f"""
                <html>
                <body>
                    <h2 style="color: #333;">Reminder: Upcoming Event</h2>
                    <p>Dear {member_email},</p>
                    <p>This is a friendly reminder that the event <strong>"{event.title}"</strong> is happening soon. Here are the details:</p>
                    <ul>
                        <li><strong>Event Title:</strong> {event.title}</li>
                        <li><strong>Date & Time:</strong> {reminder_time.strftime('%Y-%m-%d at %H:%M:%S')}</li>
                        <li><strong>Location:</strong> {event.location or 'Not specified'}</li>
                        <li><strong style="color: red;">Room ID: {event.id}</strong></li>
                    </ul>
                    <p>Don't forget to join us! We look forward to seeing you at the event.</p>
                    <br>
                    <p><strong>Best regards,</strong></p>
                    <p>The Event Team</p>
                </body>
                </html>
                """

                plaintext_body = f"""
                Reminder: Upcoming Event

                Dear {member_email},

                This is a friendly reminder that the event "{event.title}" is happening soon. Here are the details:

                Event Title: {event.title}
                Date & Time: {reminder_time.strftime('%Y-%m-%d at %H:%M:%S')}
                Location: {event.location or 'Not specified'}
                Room ID: {event.id}

                Don't forget to join us! We look forward to seeing you at the event.

                Best regards,
                The Event Team
                """

                # Send email with both HTML and plaintext content
                send_email(
                    subject=f"Reminder: Upcoming Event - {event.title}",
                    recipient=member_email,
                    plain_body=plaintext_body,
                    html_body=html_body  # Adding HTML formatted content
                )

                logger.info(f"Event reminder email sent to {member_email} for event {event_id} scheduled at {reminder_time}.")
            else:
                logger.error(f"Event with id {event_id} not found.")
    except Exception as e:
        logger.error(f"Error in send_event_reminder_email task: {str(e)}")



# Task to send event reminder emails to members (general reminder task)
@celery_app.task
def send_reminder():
    """
    Check for upcoming event reminders and send reminder emails to members.
    """
    try:
        with SessionLocal() as db:
            # Get the current time in UTC
            current_time = datetime.now(timezone.utc)

            # Define the time window (5 minutes from the current time)
            time_window_start = current_time
            time_window_end = current_time + timedelta(minutes=5)

            # Fetch reminders where reminder_time is within the next 5 minutes
            reminders = db.query(Reminder).filter(
                Reminder.reminder_time >= time_window_start,
                Reminder.reminder_time <= time_window_end
            ).all()

            if reminders:
                for reminder in reminders:
                    email = reminder.user_email.strip()
                    if email:
                        # Prepare HTML and Plaintext bodies
                        html_body = f"""
                        <html>
                        <body>
                            <h2 style="color: #333;">Reminder: Your Event '{reminder.event.title}' is Happening Soon!</h2>
                            <p>Dear {email},</p>
                            <p>This is a reminder for the upcoming event:</p>
                            <ul>
                                <li><strong>Event Title:</strong> {reminder.event.title}</li>
                                <li><strong>Date & Time:</strong> {reminder.reminder_time.strftime('%Y-%m-%d at %H:%M:%S')}</li>
                                <li><strong>Location:</strong> {reminder.event.location or 'Not specified'}</li>
                                <li><strong style="color: red;">Room ID: {reminder.event.id}</strong></li>
                            </ul>
                            <p>We look forward to your participation! Please make sure to mark your calendar.</p>
                            <br>
                            <p><strong>Best regards,</strong></p>
                            <p>The Event Team</p>
                        </body>
                        </html>
                        """

                        plaintext_body = f"""
                        Reminder: Your Event '{reminder.event.title}' is Happening Soon!

                        Dear {email},

                        This is a reminder for the upcoming event:

                        Event Title: {reminder.event.title}
                        Date & Time: {reminder.reminder_time.strftime('%Y-%m-%d at %H:%M:%S')}
                        Location: {reminder.event.location or 'Not specified'}
                        Room ID: {reminder.event.id}

                        We look forward to your participation! Please make sure to mark your calendar.

                        Best regards,
                        The Event Team
                        """

                        # Send email with both HTML and plaintext content
                        send_email(
                            subject=f"Reminder: Your Event '{reminder.event.title}' is Happening Soon!",
                            recipient=email,
                            plain_body=plaintext_body,
                            html_body=html_body  # Adding HTML formatted content
                        )

                        # After sending the email, delete the reminder entry
                        delete_reminder_entry(db, reminder.id)
                    else:
                        logger.warning(f"Skipping reminder for event {reminder.event_id} due to invalid email: {email}")
            else:
                logger.info("No upcoming reminders to send.")
    except Exception as e:
        logger.error(f"Error in send_reminder task: {str(e)}")
