import uuid

from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        supplied_id = request.headers.get("X-Request-ID", "").strip()
        # Bound and sanitize caller-provided IDs; otherwise generate a UUID.
        if supplied_id and len(supplied_id) <= 128 and all(
            char.isalnum() or char in "-_." for char in supplied_id
        ):
            request_id = supplied_id
        else:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
