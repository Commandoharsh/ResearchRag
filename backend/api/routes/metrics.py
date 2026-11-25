from fastapi import APIRouter

from backend.observability.metrics import snapshot

router = APIRouter(prefix="/metrics", tags=["Observability"])


@router.get("")
def get_metrics():
    """Return process-local request counts and latency aggregates."""
    return {"service": "ResearchRAG", "scope": "process", **snapshot()}
