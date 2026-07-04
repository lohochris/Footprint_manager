"""
Shared constants for Footprint Manager.

This package centralises all cross-cutting constant values used throughout
the platform.  Feature-specific constants belong in their respective app
packages; only truly global values live here.
"""

from __future__ import annotations

from backend.shared.constants.feature_flags import (
    ENABLE_AI,
    ENABLE_COMPLIANCE,
    ENABLE_DISCOVERY,
    ENABLE_GRAPH,
    ENABLE_REPORTING,
    FEATURE_FLAG_DEFINITIONS,
    FEATURE_FLAG_NAMES,
    FeatureFlag,
    get_feature_flags,
    is_feature_enabled,
)

# ---------------------------------------------------------------------------
# API versioning
# ---------------------------------------------------------------------------

API_VERSION: str = "v1"
"""Current stable API version prefix (e.g. /api/v1/)."""

API_BASE_PATH: str = f"/api/{API_VERSION}"
"""Fully-qualified base path for all versioned API routes."""

# ---------------------------------------------------------------------------
# Pagination defaults
# ---------------------------------------------------------------------------

DEFAULT_PAGE_SIZE: int = 25
"""Default number of records returned per page."""

MAX_PAGE_SIZE: int = 100
"""Hard upper limit on records that can be requested per page."""

MIN_PAGE_SIZE: int = 1
"""Minimum records per page request."""

DEFAULT_CURSOR_KEY: str = "cursor"
"""Default query-parameter name for cursor-based pagination."""

# ---------------------------------------------------------------------------
# HTTP / Content types
# ---------------------------------------------------------------------------

CONTENT_TYPE_JSON: str = "application/json"
CONTENT_TYPE_FORM: str = "multipart/form-data"
CONTENT_TYPE_TEXT: str = "text/plain; charset=utf-8"

# ---------------------------------------------------------------------------
# Header names (HTTP_ prefix used by Django's META dict)
# ---------------------------------------------------------------------------

HEADER_REQUEST_ID: str = "X-Request-ID"
HEADER_CORRELATION_ID: str = "X-Correlation-ID"
HEADER_API_VERSION: str = "X-API-Version"
HEADER_TENANT_ID: str = "X-Tenant-ID"

# ---------------------------------------------------------------------------
# Cache key prefixes (avoid collisions between features)
# ---------------------------------------------------------------------------

CACHE_PREFIX_HEALTH: str = "health"
CACHE_PREFIX_SESSION: str = "session"
CACHE_PREFIX_RATE_LIMIT: str = "rate_limit"
CACHE_PREFIX_FEATURE_FLAG: str = "feature_flag"

# ---------------------------------------------------------------------------
# Datetime formats
# ---------------------------------------------------------------------------

ISO8601_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"
"""ISO 8601 UTC datetime string format."""

DATE_FORMAT: str = "%Y-%m-%d"

# ---------------------------------------------------------------------------
# File / upload constraints
# ---------------------------------------------------------------------------

MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
ALLOWED_IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
)
ALLOWED_DOCUMENT_EXTENSIONS: frozenset[str] = frozenset(
    {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".md"}
)

__all__ = [
    "API_VERSION",
    "API_BASE_PATH",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MIN_PAGE_SIZE",
    "DEFAULT_CURSOR_KEY",
    "CONTENT_TYPE_JSON",
    "CONTENT_TYPE_FORM",
    "CONTENT_TYPE_TEXT",
    "HEADER_REQUEST_ID",
    "HEADER_CORRELATION_ID",
    "HEADER_API_VERSION",
    "HEADER_TENANT_ID",
    "CACHE_PREFIX_HEALTH",
    "CACHE_PREFIX_SESSION",
    "CACHE_PREFIX_RATE_LIMIT",
    "CACHE_PREFIX_FEATURE_FLAG",
    "ISO8601_FORMAT",
    "DATE_FORMAT",
    "MAX_UPLOAD_SIZE_BYTES",
    "ALLOWED_IMAGE_EXTENSIONS",
    "ALLOWED_DOCUMENT_EXTENSIONS",
    "FeatureFlag",
    "FEATURE_FLAG_DEFINITIONS",
    "FEATURE_FLAG_NAMES",
    "ENABLE_AI",
    "ENABLE_DISCOVERY",
    "ENABLE_GRAPH",
    "ENABLE_COMPLIANCE",
    "ENABLE_REPORTING",
    "get_feature_flags",
    "is_feature_enabled",
]
