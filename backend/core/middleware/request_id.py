"""Request ID middleware for distributed tracing."""

import uuid

import structlog
from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """Attach a unique request ID to each incoming HTTP request."""

    HEADER_NAME = "HTTP_X_REQUEST_ID"
    RESPONSE_HEADER = "X-Request-ID"

    def process_request(self, request: object) -> None:
        """Bind a request ID to the request and logging context."""
        request_id = getattr(request, "META", {}).get(self.HEADER_NAME)
        if not request_id:
            request_id = str(uuid.uuid4())
        request.request_id = request_id  # type: ignore[attr-defined]
        structlog.contextvars.bind_contextvars(request_id=request_id)

    def process_response(self, request: object, response: object) -> object:
        """Expose the request ID on the response headers."""
        request_id = getattr(request, "request_id", None)
        if request_id:
            response[self.RESPONSE_HEADER] = request_id  # type: ignore[index]
        structlog.contextvars.clear_contextvars()
        return response
