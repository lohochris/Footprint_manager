"""
Shared validators for Footprint Manager.

Each validator is a callable that either returns the cleaned value on success
or raises ``shared.exceptions.ValidationError`` on failure.  Validators are
intentionally framework-agnostic so they can be used in service-layer code,
Celery tasks, and DRF serializers alike.

Usage::

    from shared.validators import validate_email, validate_uuid

    clean_email = validate_email("User@Example.COM")  # returns "user@example.com"
    validate_uuid("not-a-uuid")                       # raises ValidationError
"""

from __future__ import annotations

import re
import uuid
from typing import Any

from shared.exceptions import ValidationError

# ---------------------------------------------------------------------------
# Regular expression patterns
# ---------------------------------------------------------------------------

_EMAIL_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

_SLUG_PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_URL_PATTERN: re.Pattern[str] = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}(?:\.\d{1,3}){3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

_PHONE_PATTERN: re.Pattern[str] = re.compile(r"^\+?[1-9]\d{6,14}$")


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def validate_email(value: Any) -> str:
    """
    Validate an email address string.

    Args:
        value: Raw input value.

    Returns:
        Normalised (lowercased, stripped) email address.

    Raises:
        ValidationError: If the value is not a valid email address.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"Email must be a string, got {type(value).__name__}.",
            code="INVALID_EMAIL_TYPE",
        )
    normalised = value.strip().lower()
    if not normalised:
        raise ValidationError("Email address must not be empty.", code="EMAIL_EMPTY")
    if len(normalised) > 254:
        raise ValidationError(
            "Email address exceeds maximum length of 254 characters.",
            code="EMAIL_TOO_LONG",
        )
    if not _EMAIL_PATTERN.match(normalised):
        raise ValidationError(
            f"{normalised!r} is not a valid email address.",
            code="INVALID_EMAIL_FORMAT",
        )
    return normalised


def validate_uuid(value: Any) -> uuid.UUID:
    """
    Validate and parse a UUID value.

    Args:
        value: String or UUID instance.

    Returns:
        Parsed ``uuid.UUID`` object.

    Raises:
        ValidationError: If the value is not a valid UUID.
    """
    if isinstance(value, uuid.UUID):
        return value
    if not isinstance(value, str):
        raise ValidationError(
            f"UUID must be a string or UUID instance, got {type(value).__name__}.",
            code="INVALID_UUID_TYPE",
        )
    try:
        return uuid.UUID(value.strip())
    except ValueError as exc:
        raise ValidationError(
            f"{value!r} is not a valid UUID.",
            code="INVALID_UUID_FORMAT",
        ) from exc


def validate_slug(value: Any) -> str:
    """
    Validate a URL slug (lowercase alphanumeric with hyphens).

    Args:
        value: Raw input value.

    Returns:
        The validated slug string.

    Raises:
        ValidationError: If the value does not match slug format.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"Slug must be a string, got {type(value).__name__}.",
            code="INVALID_SLUG_TYPE",
        )
    value = value.strip()
    if not value:
        raise ValidationError("Slug must not be empty.", code="SLUG_EMPTY")
    if len(value) > 255:
        raise ValidationError(
            "Slug exceeds maximum length of 255 characters.", code="SLUG_TOO_LONG"
        )
    if not _SLUG_PATTERN.match(value):
        raise ValidationError(
            f"{value!r} is not a valid slug. Use lowercase letters, digits, and hyphens only.",
            code="INVALID_SLUG_FORMAT",
        )
    return value


def validate_url(value: Any) -> str:
    """
    Validate an HTTP or HTTPS URL.

    Args:
        value: Raw input value.

    Returns:
        The validated URL string.

    Raises:
        ValidationError: If the value is not a valid URL.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"URL must be a string, got {type(value).__name__}.",
            code="INVALID_URL_TYPE",
        )
    value = value.strip()
    if not value:
        raise ValidationError("URL must not be empty.", code="URL_EMPTY")
    if not _URL_PATTERN.match(value):
        raise ValidationError(
            f"{value!r} is not a valid HTTP/HTTPS URL.",
            code="INVALID_URL_FORMAT",
        )
    return value


def validate_phone(value: Any) -> str:
    """
    Validate an international phone number in E.164-like format.

    Accepts optional leading ``+`` followed by 7–15 digits.

    Args:
        value: Raw input value.

    Returns:
        The validated phone number string.

    Raises:
        ValidationError: If the value is not a valid phone number.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"Phone number must be a string, got {type(value).__name__}.",
            code="INVALID_PHONE_TYPE",
        )
    value = value.strip().replace(" ", "").replace("-", "")
    if not _PHONE_PATTERN.match(value):
        raise ValidationError(
            f"{value!r} is not a valid phone number.",
            code="INVALID_PHONE_FORMAT",
        )
    return value


def validate_non_empty_string(value: Any, *, field_name: str = "field") -> str:
    """
    Validate that a value is a non-empty string.

    Args:
        value: Raw input value.
        field_name: Name used in the error message.

    Returns:
        The stripped string value.

    Raises:
        ValidationError: If the value is not a non-empty string.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"{field_name} must be a string, got {type(value).__name__}.",
            code="INVALID_STRING_TYPE",
        )
    stripped = value.strip()
    if not stripped:
        raise ValidationError(
            f"{field_name} must not be empty.",
            code="EMPTY_STRING",
        )
    return stripped


__all__ = [
    "validate_email",
    "validate_uuid",
    "validate_slug",
    "validate_url",
    "validate_phone",
    "validate_non_empty_string",
]
