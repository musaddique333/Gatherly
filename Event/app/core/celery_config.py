from celery import Celery

from app.core.config import settings

# Create Celery instance with the necessary configurations
celery_app = Celery(
    "event_service",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND_URL,
)

# Configuring Celery using an object from app.core.celery_config
celery_app.config_from_object('app.core.celery_config')

# Automatically discover tasks in app.tasks
celery_app.autodiscover_tasks(['app.tasks'])

# Update Celery configuration with task and result serialization settings
celery_app.conf.update(
    task_serializer="json",  # Use JSON for serializing tasks
    result_serializer="json",  # Use JSON for serializing results
    accept_content=["json"],  # Accept only JSON content for tasks
    timezone="UTC",  # Set timezone to UTC
    enable_utc=True,  # Enable UTC for time-related tasks
)

# Define periodic tasks using a more readable schedule
celery_app.conf.beat_schedule = {
    'send-reminder-every-5-minutes': {
        'task': 'app.tasks.send_reminder',  # The task to execute
        'schedule': 60.0,  # Time interval in seconds (5 minutes)
    },
}