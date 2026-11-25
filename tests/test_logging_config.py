import json
import logging

from backend.observability.logging_config import JsonFormatter


def test_json_formatter_emits_structured_request_fields():
    record = logging.LogRecord(
        name="researchrag.http",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="HTTP request completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.method = "GET"
    record.path = "/health/live"
    record.status_code = 200
    record.duration_ms = 3.2

    payload = json.loads(JsonFormatter().format(record))
    assert payload["message"] == "HTTP request completed"
    assert payload["request_id"] == "req-123"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 3.2
