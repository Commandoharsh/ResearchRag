from backend.worker.celery_app import celery_app
from backend.worker.tasks import index_document


def test_celery_uses_redis_broker_and_result_backend():
    assert celery_app.conf.broker_url == "redis://redis:6379/0"
    assert celery_app.conf.result_backend == "redis://redis:6379/0"


def test_document_indexing_task_is_registered():
    assert index_document.name == "researchrag.index_document"
    assert index_document.max_retries == 3


def test_worker_uses_safe_task_serialization():
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.task_acks_late is True
    assert celery_app.conf.worker_prefetch_multiplier == 1
