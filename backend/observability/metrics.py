"""Dependency-free process-local HTTP metrics.

Metrics are intentionally low-cardinality: paths are normalized to route
templates by middleware where possible, and query strings are never recorded.
For multi-replica deployments use a shared metrics backend or OpenTelemetry.
"""
from collections import defaultdict
from threading import Lock
from typing import Any


_lock = Lock()
_requests: dict[tuple[str, str, int], int] = defaultdict(int)
_durations: dict[tuple[str, str], dict[str, float]] = defaultdict(
    lambda: {"count": 0, "sum_ms": 0.0, "max_ms": 0.0}
)


def record_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    key = (method.upper(), path, int(status_code))
    duration_key = (method.upper(), path)
    with _lock:
        _requests[key] += 1
        bucket = _durations[duration_key]
        bucket["count"] += 1
        bucket["sum_ms"] += float(duration_ms)
        bucket["max_ms"] = max(bucket["max_ms"], float(duration_ms))


def snapshot() -> dict[str, Any]:
    with _lock:
        requests = [
            {"method": method, "path": path, "status_code": status, "count": count}
            for (method, path, status), count in sorted(_requests.items())
        ]
        durations = [
            {
                "method": method,
                "path": path,
                "count": int(values["count"]),
                "sum_ms": round(values["sum_ms"], 3),
                "max_ms": round(values["max_ms"], 3),
                "average_ms": round(values["sum_ms"] / values["count"], 3),
            }
            for (method, path), values in sorted(_durations.items())
        ]
    return {"requests": requests, "durations": durations}


def reset_metrics() -> None:
    """Test helper; never call from application request handlers."""
    with _lock:
        _requests.clear()
        _durations.clear()
