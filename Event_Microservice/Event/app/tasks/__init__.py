from app.core.celery_config import celery_app
from app.models import Event, Reminder
from app.utils import send_email
from datetime import datetime, timezone, timedelta
from app.core.db import SessionLocal
from app.crud import delete_reminder_entry

import logging
from uuid import UUID

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Task to send event creation email to the organizer
@celery_app.task
def send_event_created_email(event_id: UUID, organizer_email: str):
    """
    Send an email to the event organizer confirming the event creation.

    Args:
        event_id (UUID): The ID of the created event.
        organizer_email (str): The email address of the event organizer.
    """
    try:
        with SessionLocal() as db:
            event = db.query(Event).get(event_id)
            if event:
                # Prepare HTML and Plaintext bodies
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                    <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                        <h2 style="color: #333;">Event Creation Successful!</h2>
                        <p style="color: #555; line-height: 1.6;">Hello,</p>
                        <p style="color: #555; line-height: 1.6;">Congratulations! Your event titled <strong>{event.title}</strong> has been successfully created and is now live. Below are the details for your reference:</p>
                        <ul style="list-style-type: none; padding: 0;">
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Event Title:</strong> {event.title}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Date & Time:</strong> {event.date.strftime('%Y-%m-%d at %H:%M:%S')}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Description:</strong> {event.description or 'No description provided.'}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Location:</strong> {event.location or 'Not specified'}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Room ID:</strong> <strong style="color: blue; background-color: #e7f3ff; padding: 5px; border-radius: 3px;">{event.id}</strong>
                            </li>
                        </ul>
                        <p style="color: #555; line-height: 1.6;">Thank you for using our platform, and we wish you all the best in organizing your event!</p>
                        <p style="font-weight: bold;">Best regards,</p>
                        <p>The Event Team</p>
                    </div>
                    <div style="margin-top: 20px; font-size: 0.9em; color: #777;">
                        <p>This email was sent to you because you created an event on our platform. If you have any questions, feel free to contact us.</p>
                    </div>
                </body>
                </html>
                """

                # Send email with both HTML and plaintext content
                send_email(
                    subject=f"Your Event '{event.title}' Has Been Successfully Created!",
                    recipient=organizer_email,
                    body=body 
                )

                logger.info(f"Event creation email sent to {organizer_email} for event {event_id}.")
            else:
                logger.error(f"Event with id {event_id} not found.")
    except Exception as e:
        logger.error(f"Error in send_event_created_email task: {str(e)}")



# Task to send email to the new member when added to an event
@celery_app.task
def send_member_added_email(event_id: UUID, member_email: str):
    """
    Send an email to a new member when added to an event.

    Args:
        event_id (UUID): The ID of the event the member was added to.
        member_email (str): The email address of the new member.
    """
    try:
        with SessionLocal() as db:
            event = db.query(Event).get(event_id)
            if event:
                # Prepare HTML and Plaintext bodies
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                    <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                        <h2 style="color: #333;">You’ve Been Added to an Event!</h2>
                        <p style="color: #555; line-height: 1.6;">Hi {member_email},</p>
                        <p style="color: #555; line-height: 1.6;">We are excited to inform you that you have been successfully added to the event <strong>"{event.title}"</strong>. Here are the details:</p>
                        <ul style="list-style-type: none; padding: 0;">
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Event Title:</strong> {event.title}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Date & Time:</strong> {event.date.strftime('%Y-%m-%d at %H:%M:%S')}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Description:</strong> {event.description or 'No description provided.'}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Location:</strong> {event.location or 'Not specified'}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Room ID:</strong> <strong style="color: blue; background-color: #e7f3ff; padding: 5px; border-radius: 3px;">{event.id}</strong>
                            </li>
                        </ul>
                        <p style="color: #555; line-height: 1.6;">Please mark your calendar and feel free to reach out if you have any questions.</p>
                        <p style="font-weight: bold; color: #555;">Best regards,</p>
                        <p style="color: #555;">The Event Team</p>
                    </div>
                </body>
                </html>
                """
                # Send email with both HTML and plaintext content
                send_email(
                    subject=f"You’ve Been Added to an Event '{event.title}'!",
                    recipient=member_email,
                    body=body 
                )

                logger.info(f"Member added email sent to {member_email} for event {event_id}.")
            else:
                logger.error(f"Event with id {event_id} not found.")
    except Exception as e:
        logger.error(f"Error in send_member_added_email task: {str(e)}")



# Task to send event reminder emails to members
@celery_app.task
def send_event_reminder_email(reminder_time: str, member_email: str, event_id: UUID):
    """
    Send a reminder email to a member for an event.

    Args:
        reminder_time (str): The time of the reminder in ISO format.
        member_email (str): The email address of the member to send the reminder.
        event_id (UUID): The ID of the event for the reminder.
    """
    try:
        reminder_time = datetime.fromisoformat(reminder_time)
        with SessionLocal() as db:
            event = db.query(Event).get(event_id)
            if event:
                # Prepare HTML and Plaintext bodies
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                    <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                        <h2 style="color: #333;">Reminder: Upcoming Event</h2>
                        <p style="color: #555; line-height: 1.6;">Dear {member_email},</p>
                        <p style="color: #555; line-height: 1.6;">This is a friendly reminder that the event <strong>"{event.title}"</strong> is happening soon. Here are the details:</p>
                        <ul style="list-style-type: none; padding: 0;">
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Event Title:</strong> {event.title}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Date & Time:</strong> {reminder_time.strftime('%Y-%m-%d at %H:%M:%S')}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Location:</strong> {event.location or 'Not specified'}
                            </li>
                            <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Room ID:</strong> <strong style="color: blue; background-color: #e7f3ff; padding: 5px; border-radius: 3px;">{event.id}</strong>
                            </li>
                        </ul>
                        <p style="color: #555; line-height: 1.6;">Don't forget to join us! We look forward to seeing you at the event.</p>
                        <p style="font-weight: bold; color: #555;">Best regards,</p>
                        <p style="color: #555;">The Event Team</p>
                    </div>
                </body>
                </html>
                """
                # Send email with both HTML and plaintext content
                send_email(
                    subject=f"Reminder: Upcoming Event - {event.title}",
                    recipient=member_email,
                    body=body
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
                        body = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                            <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                                <h2 style="color: #333;">Reminder: Your Event '{reminder.event.title}' is Happening Soon!</h2>
                                <p style="color: #555; line-height: 1.6;">Dear {email},</p>
                                <p style="color: #555; line-height: 1.6;">This is a reminder for the upcoming event:</p>
                                <ul style="list-style-type: none; padding: 0;">
                                    <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                        <strong>Event Title:</strong> {reminder.event.title}
                                    </li>
                                    <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                        <strong>Date & Time:</strong> {reminder.reminder_time.strftime('%Y-%m-%d at %H:%M:%S')}
                                    </li>
                                    <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                        <strong>Location:</strong> {reminder.event.location or 'Not specified'}
                                    </li>
                                    <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                <strong>Room ID:</strong> <strong style="color: blue; background-color: #e7f3ff; padding: 5px; border-radius: 3px;">{reminder.event.id}</strong>
                                    </li>
                                </ul>
                                <p style="color: #555; line-height: 1.6;">We look forward to your participation! Please make sure to mark your calendar.</p>
                                <p style="font-weight: bold; color: #555;">Best regards,</p>
                                <p style="color: #555;">The Event Team</p>
                            </div>
                        </body>
                        </html>
                        """

                        # Send email with both HTML and plaintext content
                        send_email(
                            subject=f"Reminder: Your Event '{reminder.event.title}' is Happening Soon!",
                            recipient=email,
                            body=body
                        )

                        # After sending the email, delete the reminder entry
                        delete_reminder_entry(db, reminder.id)
                    else:
                        logger.warning(f"Skipping reminder for event {reminder.event_id} due to invalid email: {email}")
            else:
                logger.info("No upcoming reminders to send.")
    except Exception as e:
        logger.error(f"Error in send_reminder task: {str(e)}")


# Task to send request acces to join the event
@celery_app.task
def send_join_request(user_email: str, organiser_email: str, event_id: UUID):
    """
    Check for upcoming event reminders and send reminder emails to members.
    """
    try:
        with SessionLocal() as db:
            # Get the event details
            event = db.query(Event).filter(Event.id == event_id).first()

            user_body = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                            <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                                <h2 style="color: #333;">Your Request to Join the Event '{event.title}' Has Been Successfully Sent!</h2>
                                <p style="color: #555; line-height: 1.6;">Dear {user_email},</p>
                                <p style="color: #555; line-height: 1.6;">We are pleased to inform you that your request to join the event <strong>'{event.title}'</strong> has been successfully sent to the event organizer.</p>
                                <p style="color: #555; line-height: 1.6;">The event details are as follows:</p>
                                <ul style="list-style-type: none; padding: 0;">
                                    <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                        <strong>Event Title:</strong> {event.title}
                                    </li>
                                    <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                        <strong>Location:</strong> {event.location or 'Not specified'}
                                    </li>
                                    <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                        <strong>Date:</strong> {event.date}
                                    </li>
                                </ul>
                                <p style="color: #555; line-height: 1.6;">The event organizer will review your request, and you will be notified if you are granted access to the event.</p>
                                <p style="font-weight: bold; color: #555;">Best regards,</p>
                                <p style="color: #555;">The Dodgygeezers Team</p>
                            </div>
                        </body>
                        </html>
                        """

            organiser_body = f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                                <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                                    <h2 style="color: #333;">New Access Request for Your Event '{event.title}'</h2>
                                    <p style="color: #555; line-height: 1.6;">Dear {organiser_email},</p>
                                    <p style="color: #555; line-height: 1.6;">You have a new request from <strong>{user_email}</strong> to join the event <strong>'{event.title}'</strong>.</p>
                                    <p style="color: #555; line-height: 1.6;">Here are the event details and user details:</p>
                                    <ul style="list-style-type: none; padding: 0;">
                                        <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                            <strong>Requested User:</strong> <strong style="color: red; background-color: #ffcccc; padding: 5px; border-radius: 3px;">{user_email}</strong>
                                        </li>
                                        <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                            <strong>Event Title:</strong> {event.title}
                                        </li>
                                        <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                            <strong>Location:</strong> {event.location or 'Not specified'}
                                        </li>
                                        <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                            <strong>Date:</strong> {event.date}
                                        </li>
                                        <li style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
                                            <strong>Room ID:</strong> <strong style="color: blue; background-color: #e7f3ff; padding: 5px; border-radius: 3px;">{event.id}</strong>
                                        </li>
                                    </ul>
                                    <p style="color: #555; line-height: 1.6;">If you wish to add this user as a member of your event, please log into your admin panel and approve their access request. You can manage participants directly within the app.</p>
                                    <p style="font-weight: bold; color: #555;">Best regards,</p>
                                    <p style="color: #555;">The Dodgygeezers Team</p>
                                </div>
                            </body>
                            </html>
                            """

            # Send email to user that acces request sent succes fully
            send_email(
                subject=f"Your Request to Join the Event '{event.title}' Has Been Successfully Sent",
                recipient=user_email,
                body=user_body
            )

            # send email to orgniser to ad approve the request
            send_email(
                subject = f"New Access Request for Your Event '{event.title}' from {user_email}",
                recipient=organiser_email,
                body=organiser_body
            ) 
    except Exception as e:
        logger.error(f"Error in send_reminder task: {str(e)}")
