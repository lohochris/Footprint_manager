"""Correlation ID middleware for cross-service tracing."""

import uuid

import structlog
from django.utils.deprecation import MiddlewareMixin


class CorrelationIDMiddleware(MiddlewareMixin):
    """Propagate or generate a correlation ID for related requests."""

    HEADER_NAME = "HTTP_X_CORRELATION_ID"
    RESPONSE_HEADER = "X-Correlation-ID"

    def process_request(self, request: object) -> None:
        """Bind a correlation ID to the request and logging context."""
        correlation_id = getattr(request, "META", {}).get(self.HEADER_NAME)
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        request.correlation_id = correlation_id  # type: ignore[attr-defined]
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    def process_response(self, request: object, response: object) -> object:
        """Expose the correlation ID on the response headers."""
        correlation_id = getattr(request, "correlation_id", None)
        if correlation_id:
            response[self.RESPONSE_HEADER] = correlation_id  # type: ignore[index]
        return response
