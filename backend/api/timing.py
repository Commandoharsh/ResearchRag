import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

from backend.observability.metrics import record_request

logger = logging.getLogger("researchrag.http")


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            elapsed = time.perf_counter() - start
            duration_ms = elapsed * 1000
            request_id = getattr(request.state, "request_id", "unknown")
            path = request.url.path
            record_request(request.method, path, status_code, duration_ms)
            logger.info(
                "HTTP request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 3),
                },
            )
            response.headers["X-Process-Time"] = f"{elapsed:.3f}"
            return response
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            request_id = getattr(request.state, "request_id", "unknown")
            record_request(request.method, request.url.path, status_code, elapsed)
            logger.exception(
                "HTTP request raised an unhandled exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(elapsed, 3),
                },
            )
            raise
