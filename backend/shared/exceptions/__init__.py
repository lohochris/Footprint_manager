"""
Shared exception hierarchy for Footprint Manager.

All custom exceptions inherit from ``FootprintBaseException`` so that
catch-all error handlers can distinguish platform exceptions from
unexpected third-party or stdlib errors.

Usage::

    from shared.exceptions import NotFoundError, ValidationError

    raise NotFoundError("Investigation not found", code="INVESTIGATION_NOT_FOUND")
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any


class FootprintBaseException(Exception):
    """
    Root exception class for all Footprint Manager platform errors.

    Attributes:
        message: Human-readable description of the error.
        code: Machine-readable error code for client consumers.
        status_code: Suggested HTTP status code for API responses.
        detail: Optional structured detail payload.
    """

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    default_code: str = "INTERNAL_ERROR"
    default_message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        detail: Any = None,
    ) -> None:
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.detail = detail
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(code={self.code!r}, message={self.message!r})"


class ValidationError(FootprintBaseException):
    """Raised when input data fails validation rules."""

    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    default_code = "VALIDATION_ERROR"
    default_message = "The submitted data is invalid."


class NotFoundError(FootprintBaseException):
    """Raised when a requested resource cannot be located."""

    status_code = HTTPStatus.NOT_FOUND
    default_code = "NOT_FOUND"
    default_message = "The requested resource was not found."


class PermissionDeniedError(FootprintBaseException):
    """Raised when a caller lacks the required permission for an action."""

    status_code = HTTPStatus.FORBIDDEN
    default_code = "PERMISSION_DENIED"
    default_message = "You do not have permission to perform this action."


class AuthenticationError(FootprintBaseException):
    """Raised when a request cannot be authenticated."""

    status_code = HTTPStatus.UNAUTHORIZED
    default_code = "AUTHENTICATION_REQUIRED"
    default_message = "Authentication credentials were not provided or are invalid."


class ConflictError(FootprintBaseException):
    """Raised when an operation conflicts with the current resource state."""

    status_code = HTTPStatus.CONFLICT
    default_code = "CONFLICT"
    default_message = "The request conflicts with the current state of the resource."


class RateLimitError(FootprintBaseException):
    """Raised when a caller has exceeded their request rate limit."""

    status_code = HTTPStatus.TOO_MANY_REQUESTS
    default_code = "RATE_LIMIT_EXCEEDED"
    default_message = "Too many requests. Please try again later."


class ServiceUnavailableError(FootprintBaseException):
    """Raised when a downstream service or dependency is unavailable."""

    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    default_code = "SERVICE_UNAVAILABLE"
    default_message = "A required service is currently unavailable."


class ConfigurationError(FootprintBaseException):
    """Raised when the application is misconfigured at startup or runtime."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_code = "CONFIGURATION_ERROR"
    default_message = "The application is not correctly configured."


class IntegrationError(FootprintBaseException):
    """Raised when a third-party integration call fails."""

    status_code = HTTPStatus.BAD_GATEWAY
    default_code = "INTEGRATION_ERROR"
    default_message = "An external integration call failed."


class StorageError(FootprintBaseException):
    """Raised when a file storage operation fails."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_code = "STORAGE_ERROR"
    default_message = "A storage operation failed."


class EventDispatchError(FootprintBaseException):
    """Raised when a domain event cannot be dispatched."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_code = "EVENT_DISPATCH_ERROR"
    default_message = "Failed to dispatch domain event."


__all__ = [
    "FootprintBaseException",
    "ValidationError",
    "NotFoundError",
    "PermissionDeniedError",
    "AuthenticationError",
    "ConflictError",
    "RateLimitError",
    "ServiceUnavailableError",
    "ConfigurationError",
    "IntegrationError",
    "StorageError",
    "EventDispatchError",
]
