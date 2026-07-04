"""
Shared pagination utilities for Footprint Manager.

Provides:
- ``PagedResult`` — generic typed dataclass for paginated API responses
- ``CursorPage`` — cursor-based pagination metadata
- ``FootprintPageNumberPagination`` — DRF paginator aligned with platform conventions

Usage::

    from backend.shared.pagination import FootprintPageNumberPagination, PagedResult
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from backend.shared.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


@dataclass(frozen=True)
class PagedResult(Generic[T]):
    """
    Generic paginated result wrapper.

    Attributes:
        items: The records for the current page.
        total: Total number of matching records across all pages.
        page: Current 1-based page number.
        page_size: Number of records per page.
        has_next: Whether a subsequent page exists.
        has_previous: Whether a preceding page exists.
    """

    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

    @property
    def total_pages(self) -> int:
        """Computed total number of pages."""
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


@dataclass(frozen=True)
class CursorPage(Generic[T]):
    """
    Cursor-based paginated result — recommended for high-volume feeds.

    Attributes:
        items: Records for the current window.
        next_cursor: Opaque token for retrieving the next page (None if last page).
        previous_cursor: Opaque token for retrieving the previous page (None if first).
        has_next: Whether more records follow.
        has_previous: Whether records precede this window.
    """

    items: list[T]
    next_cursor: str | None
    previous_cursor: str | None
    has_next: bool
    has_previous: bool
    meta: dict[str, Any] = field(default_factory=dict)


def encode_cursor(payload: dict[str, Any]) -> str:
    """Encode a cursor payload dict into a URL-safe base64 token."""
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(token: str) -> dict[str, Any]:
    """Decode a cursor token back into its payload dict."""
    raw = base64.urlsafe_b64decode(token.encode()).decode()
    return json.loads(raw)


class FootprintPageNumberPagination(PageNumberPagination):
    """
    Platform-standard DRF page-number paginator.

    Query parameters:
        page      — 1-based page number (default: 1)
        page_size — Records per page (default: 25, max: 100)

    Response envelope includes ``count``, ``next``, ``previous``, ``results``.
    """

    page_size = DEFAULT_PAGE_SIZE
    max_page_size = MAX_PAGE_SIZE
    page_size_query_param = "page_size"
    page_query_param = "page"

    def get_paginated_response(self, data: list[Any]) -> Response:
        if self.page is None:
            raise RuntimeError("Pagination response requested before paginate_queryset.")
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "object",
            "required": ["count", "results"],
            "properties": {
                "count": {"type": "integer", "description": "Total record count"},
                "next": {"type": "string", "nullable": True, "format": "uri"},
                "previous": {"type": "string", "nullable": True, "format": "uri"},
                "page": {"type": "integer"},
                "total_pages": {"type": "integer"},
                "results": schema,
            },
        }

    def paginate_queryset(
        self, queryset: Any, request: Request, view: Any = None
    ) -> list[Any] | None:  # type: ignore[override]
        return super().paginate_queryset(queryset, request, view)


__all__ = [
    "PagedResult",
    "CursorPage",
    "encode_cursor",
    "decode_cursor",
    "FootprintPageNumberPagination",
]
