"""
Celery Configuration for Async Task Processing
"""
from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    'booking_tasks',
    broker=getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
    backend=getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
    include=['app.tasks']  # Import tasks module so they get registered
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,
    task_ignore_result=True,  # We don't need to store results
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    'app.tasks.send_booking_notification': {'queue': 'notifications'},
}
