from fastapi import APIRouter
from app.api.routes import events

api_router = APIRouter()

# Include event-related routes
api_router.include_router(events.router, prefix="/events", tags=["events"])
