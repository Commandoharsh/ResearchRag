"""Celery application for asynchronous ResearchRAG jobs."""
import os

from celery import Celery

from backend.observability.logging_config import configure_logging

configure_logging()
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "researchrag",
    broker=redis_url,
    backend=redis_url,
    include=["backend.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    worker_hijack_root_logger=False,
    result_expires=3600,
)
