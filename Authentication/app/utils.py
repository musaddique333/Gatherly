import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from app.core.config import settings


# Function to validate email domain (for corporates)
def is_corporate_email(email: str):
    personal_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
    if any(email.endswith(domain) for domain in personal_domains):
        raise HTTPException(status_code=400, detail="Corporate email cannot be from personal providers (e.g., Gmail).")
    return True

# Phone number validation (E.164 format)
def is_valid_phone_number(phone_number: str):
    pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(pattern, phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    return True

# Email utility
def send_verification_email(to_email: str, verification_link: str):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = 'Verify your email to register into Tag-ID'

    body = f'Click on the link to verify your email: {verification_link}'
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)

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

