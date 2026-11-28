from backend.observability.metrics import record_request, reset_metrics, snapshot


def setup_function():
    reset_metrics()


def test_metrics_track_request_counts_and_latency():
    record_request("get", "/health/live", 200, 12.5)
    record_request("GET", "/health/live", 200, 7.5)
    record_request("POST", "/query", 500, 30)

    result = snapshot()
    live = next(item for item in result["requests"] if item["path"] == "/health/live")
    assert live["count"] == 2

    latency = next(item for item in result["durations"] if item["path"] == "/health/live")
    assert latency["count"] == 2
    assert latency["sum_ms"] == 20
    assert latency["average_ms"] == 10
    assert latency["max_ms"] == 12.5


def test_metrics_snapshot_is_empty_after_reset():
    assert snapshot() == {"requests": [], "durations": []}
