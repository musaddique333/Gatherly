from celery import Celery
from app.core.config import settings

# Create a Celery instance
celery_app = Celery(
    "event_service",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
)

celery_app.config_from_object('app.core.celery_config')
celery_app.autodiscover_tasks(['app.tasks'])


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Define periodic tasks
celery_app.conf.beat_schedule = {
    'send-reminder-every-minute': {
        'task': 'app.tasks.send_reminder',
        'schedule': 300.0,
    },
}