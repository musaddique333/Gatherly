import re
import smtplib
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from app.core.config import settings


# Phone number validation (E.164 format)
def is_valid_phone_number(phone_number: str):
    pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(pattern, phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    return True


# Password strength utility
def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    
    if not re.search(r'\d', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    
    if not re.search(r'[@$!%*?&]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character (@, $, !, %, *, ?, &).")

    return True

# Phone Number utility
def send_sms(phone_number: str, message: str):
    #NOTE: Twilio or another service to send SMS
    pass  # TODO: implemnt the logic of otp

# Email utility
def send_verification_email(to_username:str, to_email: str, verification_link: str):
    msg = MIMEMultipart()
    msg['From'] = 'Dodgygeezers.co<' + settings.EMAIL_FROM + '>'
    msg['To'] = to_username + '<' + to_email + '>'
    msg['Subject'] = 'Verify your email to register into dodgygeezers'

    body = f"""
    Hello,

    Thank you for registering with DodgyGeezers! We're excited to have you on board.

    To complete your registration, please verify your email address by clicking the link below:

    {verification_link}

    If you did not sign up for this account, please ignore this email. If you have any questions or need assistance, feel free to reach out to us.

    Best regards,
    The DodgyGeezers Team

    If the button above doesn't work, please copy and paste the following URL into your browser:
    {verification_link}
    """
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# JWT token utility
def generate_verification_token(email: str) -> str:
    return serializer.dumps(email, salt="email-verification")

# decode JWT utility
def decode_verification_token(token: str, max_age: int = 600) -> str:
    try:
        return serializer.loads(token, salt="email-verification", max_age=max_age)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="The verification link has expired.")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid verification link.")