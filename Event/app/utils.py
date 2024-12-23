import httpx
from fastapi import HTTPException
from app.core.config import settings
import os

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://registration:8000")


def validate_user(email: str):
    url = f"{AUTH_SERVICE_URL}/auth/validate-user/{email}"  # Replace with the actual endpoint for user retrieval
    try:
        response = httpx.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
