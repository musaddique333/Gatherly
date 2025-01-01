import re
import smtplib
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException

from app.core.config import settings


# Phone number validation (E.164 format)
def is_valid_phone_number(phone_number: str) -> bool:
    """
    Validates if the phone number is in the correct E.164 format.
    
    The E.164 format is defined as a '+' sign followed by up to 15 digits, 
    with no spaces or other characters allowed.

    Args:
    - phone_number (str): The phone number to validate.

    Returns:
    - bool: True if the phone number is valid.

    Raises:
    - HTTPException: If the phone number format is invalid.
    """
    pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(pattern, phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    return True


# Password strength utility
def validate_password_strength(password: str) -> bool:
    """
    Validates the strength of the password based on specific criteria:
    - Minimum length of 8 characters.
    - At least one uppercase letter.
    - At least one lowercase letter.
    - At least one digit.
    - At least one special character (@, $, !, %, *, ?, &).

    Args:
    - password (str): The password to validate.

    Returns:
    - bool: True if the password meets all strength criteria.

    Raises:
    - HTTPException: If the password does not meet any of the criteria.
    """
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    
    if not re.search(r'\d', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    
    if not re.search(r'[@$!%*?&#]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character (@, $, !, %, *, ?, &).")

    return True

# Phone Number utility
def send_sms(phone_number: str, message: str):
    #NOTE: Twilio or another service to send SMS
    pass  # TODO: implemnt the logic of otp

# Email utility
def send_verification_email(to_username: str, to_email: str, verification_link: str):
    """
    Sends a verification email to the user with a registration link.

    Args:
    - to_username (str): The username of the recipient.
    - to_email (str): The email address of the recipient.
    - verification_link (str): The link the recipient needs to click to verify their email.

    Raises:
    - SMTPException: If an error occurs while sending the email.
    """
    msg = MIMEMultipart()
    msg['From'] = f'Dodgygeezers.co<{settings.EMAIL_FROM}>'
    msg['To'] = f'{to_username}<{to_email}>'
    msg['Subject'] = 'Verify your email to register into DodgyGeezers'
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333;">Hello {to_username},</h2>
            <p style="color: #555; line-height: 1.6;">Thank you for registering with DodgyGeezers! We're excited to have you on board.</p>
            <p style="color: #555; line-height: 1.6;">To complete your registration, please verify your email address by clicking the button below:</p>
            <a href="{verification_link}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #007BFF; text-decoration: none; border-radius: 5px; margin: 10px 0;">Verify Email</a>
            <p style="color: #555; line-height: 1.6;">If you did not sign up for this account, please ignore this email. If you have any questions or need assistance, feel free to reach out to us.</p>
            <p style="font-weight: bold; color: #555;">Best regards,<br>The DodgyGeezers Team</p>
            <p style="color: #555; line-height: 1.6;">If the button above doesn't work, please copy and paste the following URL into your browser:<br>
            <a href="{verification_link}" style="color: #007BFF; text-decoration: none;">{verification_link}</a></p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")
        raise  # Re-raise the exception for higher-level handling


# Serializer instance
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# JWT token utility
def generate_verification_token(email: str) -> str:
    """
    Generates a time-sensitive token for email verification.

    Args:
    - email (str): The email address of the user to generate the verification token for.

    Returns:
    - str: The generated token.

    Raises:
    - Exception: If the token cannot be generated.
    """
    try:
        return serializer.dumps(email, salt="email-verification")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating verification token: {str(e)}")

# decode JWT utility
def decode_verification_token(token: str, max_age: int = 600) -> str:
    """
    Decodes a verification token and returns the associated email address.

    Args:
    - token (str): The verification token to decode.
    - max_age (int): The maximum age of the token in seconds. Default is 600 seconds (10 minutes).

    Returns:
    - str: The email address associated with the verification token.

    Raises:
    - HTTPException: If the token is expired or invalid.
    """
    try:
        return serializer.loads(token, salt="email-verification", max_age=max_age)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="The verification link has expired.")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid verification link.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decoding verification token: {str(e)}")