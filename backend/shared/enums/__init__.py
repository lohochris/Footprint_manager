"""
Shared enumerations for Footprint Manager.

All platform-wide enum values are defined here.  Domain-specific enums
(e.g. investigation status) belong inside their respective app packages.
"""

from __future__ import annotations

from enum import StrEnum


class SortDirection(StrEnum):
    """Sort order for paginated query results."""

    ASC = "asc"
    DESC = "desc"


class EntityStatus(StrEnum):
    """Generic lifecycle status applicable to many domain entities."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"
    DELETED = "deleted"


class LogLevel(StrEnum):
    """Application log severity levels (mirrors Python logging names)."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(StrEnum):
    """Deployment environment identifiers."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ContentType(StrEnum):
    """Supported media / MIME content types used in API responses."""

    JSON = "application/json"
    CSV = "text/csv"
    PDF = "application/pdf"
    OCTET_STREAM = "application/octet-stream"


class HttpMethod(StrEnum):
    """HTTP verb constants for routing and validation."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class CacheStrategy(StrEnum):
    """Cache invalidation / write strategies."""

    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"
    READ_THROUGH = "read_through"


__all__ = [
    "SortDirection",
    "EntityStatus",
    "LogLevel",
    "Environment",
    "ContentType",
    "HttpMethod",
    "CacheStrategy",
]
