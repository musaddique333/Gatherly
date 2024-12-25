import grpc
from app.api import auth_pb2, auth_pb2_grpc
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def validate_user(email: str):
    """
    Validates the user email by calling an external authentication service via gRPC.

    Args:
        email (str): The email address of the user to validate.

    Raises:
        HTTPException: If the user is not found or if there is a gRPC communication issue.
    """
    try:
        # Set up the gRPC channel and client
        channel = grpc.insecure_channel(f"{settings.AUTH_SERVICE_HOST}:{settings.AUTH_SERVICE_PORT}")
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        request = auth_pb2.ValidateUserRequest(email=email)
        
        # Send request to validate user
        response = stub.ValidateUser(request)
        
        # Check if the response indicates a valid user
        if not response.is_valid:
            logger.warning(f"User {email} not found.")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User {email} validated successfully.")
    
    except grpc.RpcError as e:
        logger.error(f"gRPC error while validating user {email}: {e.details()}")
        raise HTTPException(status_code=503, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"Unexpected error during user validation: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error during user validation")

def send_email(subject: str, recipient: str, plain_body: str, html_body: str):
    """
    Sends an email using SMTP.

    Args:
        subject (str): The subject of the email.
        recipient (str): The recipient's email address.
        body (str): The body content of the email.

    Raises:
        Exception: If the email fails to send.
    """
    msg = MIMEMultipart()
    msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    msg['To'] = f"Subscriber <{recipient}>"
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, "html"))
    msg.attach(MIMEText(plain_body, "plain"))

    try:
        # Set up the SMTP server and send email
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            logger.info(f"Email sent to {recipient} with subject '{subject}'")
    
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while sending email: {str(e)}")
        raise Exception(f"Unexpected error while sending email: {str(e)}")
