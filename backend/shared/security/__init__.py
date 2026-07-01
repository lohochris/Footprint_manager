"""
Shared security context and token utilities for Footprint Manager.

Provides:
- ``SecurityContext`` — request-scoped security principal carrier
- ``TokenClaims`` — typed dataclass for JWT claim extraction
- ``mask_value`` — utility for redacting sensitive strings in logs

No cryptographic implementation is performed here.  Concrete JWT handling
is done by ``rest_framework_simplejwt``.  This module provides typed
wrappers and helpers for the rest of the codebase to consume.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class TokenClaims:
    """
    Typed representation of decoded JWT claims.

    Attributes:
        user_id: The authenticated user's UUID.
        email: The authenticated user's email address.
        token_type: "access" or "refresh".
        jti: JWT ID — unique token identifier for revocation tracking.
        exp: Unix epoch timestamp of token expiry.
        extra: Any additional claims not explicitly mapped above.
    """

    user_id: UUID
    email: str
    token_type: str
    jti: str
    exp: int
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityContext:
    """
    Request-scoped security principal carrier.

    Populated by authentication middleware and passed through the service
    layer.  Never store this on long-lived objects.

    Attributes:
        user_id: Authenticated user UUID (None for anonymous).
        email: Authenticated user email.
        is_authenticated: Whether the request has a valid identity.
        is_service_account: Whether the caller is a machine client.
        tenant_id: Organisation UUID for tenant-isolated operations.
        request_id: Distributed trace request ID.
        correlation_id: Distributed trace correlation ID.
        scopes: Set of OAuth-style permission scopes granted to the token.
    """

    user_id: UUID | None = None
    email: str | None = None
    is_authenticated: bool = False
    is_service_account: bool = False
    tenant_id: UUID | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    scopes: frozenset[str] = field(default_factory=frozenset)

    def has_scope(self, scope: str) -> bool:
        """Return True if the granted scopes include *scope*."""
        return scope in self.scopes

    @classmethod
    def anonymous(cls) -> SecurityContext:
        """Return a fully unauthenticated context."""
        return cls(is_authenticated=False)


# ---------------------------------------------------------------------------
# Sensitive value masking
# ---------------------------------------------------------------------------

_MASK_PATTERN: re.Pattern[str] = re.compile(
    r"(password|secret|token|key|auth|credential|api_key|private)",
    re.IGNORECASE,
)


def mask_value(value: str, *, visible_chars: int = 4) -> str:
    """
    Redact all but the first *visible_chars* characters of a sensitive string.

    Args:
        value: The sensitive string to mask.
        visible_chars: Number of leading characters to leave visible.

    Returns:
        A masked string such as ``"sk-1****"``.
    """
    if not value:
        return ""
    visible = value[:visible_chars]
    return f"{visible}{'*' * max(0, len(value) - visible_chars)}"


def is_sensitive_key(key: str) -> bool:
    """Return True if *key* looks like it holds sensitive data."""
    return bool(_MASK_PATTERN.search(key))


def hash_identifier(value: str) -> str:
    """
    Return a SHA-256 hex digest of *value* for safe logging without exposing PII.

    Args:
        value: The identifier to hash (e.g. email, IP address).

    Returns:
        64-character hex string.
    """
    return hashlib.sha256(value.encode()).hexdigest()


__all__ = [
    "TokenClaims",
    "SecurityContext",
    "mask_value",
    "is_sensitive_key",
    "hash_identifier",
]
