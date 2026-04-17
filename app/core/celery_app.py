from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "sec_analyzer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True
)

celery_app.autodiscover_tasks([
    "app.tasks.fetch_tasks",
    "app.tasks.embedding_tasks",
    "app.tasks.topic_tasks"
])
