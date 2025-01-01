from fastapi import FastAPI

from app.api.main import api_router
from app.core.db import engine, Base
from app.core.celery_config import celery_app
from app.tasks import send_event_created_email, send_member_added_email, send_event_reminder_email, send_reminder
from app.services.wait_for_postgres import wait_for_postgres
from app.services.wait_for_redis import wait_for_redis

# Wait for PostgreSQL and Redis to be ready before starting the app
wait_for_postgres()
wait_for_redis()

# Create FastAPI app instance
app = FastAPI(
    title="Dodgygeezers Event",
    on_startup=[celery_app.control.purge]  # Purge any existing tasks in the Celery queue on startup
)

# Ensure all database tables are created in Supabase
Base.metadata.create_all(bind=engine)

# Include the API routes from the main router
app.include_router(api_router)

@app.get("/")
def read_root():
    """
    Root endpoint to confirm that the API is running.

    This endpoint serves as a simple health check, indicating that the 
    server is up and running.

    Returns:
        dict: A welcome message indicating the service is operational.
    """
    return {"message": "Welcome to the Dodgygeezers Event"}
