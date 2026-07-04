"""
Shared type aliases for Footprint Manager.

Centralises commonly-used type hints so that the rest of the codebase
imports them from a single authoritative location.  This avoids scattered
re-definitions and makes refactoring easier.

Usage::

    from backend.shared.types import UUID4, ISODatetime, JSONDict, PositiveInt
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

# ---------------------------------------------------------------------------
# Primitive aliases
# ---------------------------------------------------------------------------

UUID4 = UUID
"""A UUID version 4 identifier."""

ISODatetime = datetime
"""A timezone-aware datetime in ISO 8601 format."""

JSONDict = dict[str, Any]
"""Arbitrary JSON-serialisable dictionary."""

JSONList = list[Any]
"""Arbitrary JSON-serialisable list."""

PositiveInt = int
"""An integer that must be > 0 (enforced at the call site)."""

NonNegativeInt = int
"""An integer that must be >= 0 (enforced at the call site)."""

Slug = str
"""A URL-safe lowercase slug string (validated by shared.validators.validate_slug)."""

EmailStr = str
"""An email address string (validated by shared.validators.validate_email)."""

UrlStr = str
"""An HTTP/HTTPS URL string (validated by shared.validators.validate_url)."""

TenantID = UUID
"""Organisation UUID used for multi-tenant isolation."""

UserID = UUID
"""Authenticated user UUID."""

# ---------------------------------------------------------------------------
# Structured payloads
# ---------------------------------------------------------------------------

Headers = dict[str, str]
"""HTTP header dictionary (name → value)."""

QueryParams = dict[str, str | list[str]]
"""URL query parameter dictionary."""

ErrorDetail = dict[str, Any]
"""Structured error detail payload included in API error responses."""

__all__ = [
    "UUID4",
    "ISODatetime",
    "JSONDict",
    "JSONList",
    "PositiveInt",
    "NonNegativeInt",
    "Slug",
    "EmailStr",
    "UrlStr",
    "TenantID",
    "UserID",
    "Headers",
    "QueryParams",
    "ErrorDetail",
]
