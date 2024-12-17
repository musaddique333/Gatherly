import httpx
from fastapi import HTTPException
from app.core.config import settings

AUTH_SERVICE_URL = "http://127.0.0.1:8000"  # Adjust to your Authentication service URL

def validate_user(user_id: int):
    url = f"{AUTH_SERVICE_URL}/users/{user_id}"  # Replace with the actual endpoint for user retrieval
    try:
        response = httpx.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
