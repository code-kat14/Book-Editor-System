from celery import Celery
import os

CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "book_edit",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
)
celery_app.autodiscover_tasks(["pipeline.task"])

