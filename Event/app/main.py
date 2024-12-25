from fastapi import FastAPI
from app.api.main import api_router
from app.core.db import engine, Base
from app.core.celery_config import celery_app
from app.tasks import send_event_created_email, send_member_added_email, send_event_reminder_email, send_reminder

from app.services.wait_for_postgres import wait_for_postgres
from app.services.wait_for_redis import wait_for_redis
wait_for_postgres()
wait_for_redis()

app = FastAPI(title="Dodgygeezers Event", on_startup=[celery_app.control.purge])

# Create all database tables in Supabase
Base.metadata.create_all(bind=engine)

# Include the API routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Dodgygeezers Event"}
