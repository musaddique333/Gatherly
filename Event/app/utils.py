import grpc
from app.api import auth_pb2, auth_pb2_grpc
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def validate_user(email: str):
    try:
        channel = grpc.insecure_channel(f"{settings.AUTH_SERVICE_HOST}:{settings.AUTH_SERVICE_PORT}")
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        request = auth_pb2.ValidateUserRequest(email=email)
        response = stub.ValidateUser(request)
        if not response.is_valid:
            raise HTTPException(status_code=404, detail="User not found")
    except grpc.RpcError as e:
        raise HTTPException(status_code=503, detail=f"gRPC error: {e.details()}")
    
def send_email(subject: str, recipient: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = 'Dodgygeezers.co<' + settings.EMAIL_FROM + '>'
    msg['To'] = 'Subscriber' + '<' + recipient + '>'
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")