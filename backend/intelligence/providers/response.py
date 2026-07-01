# backend/intelligence/providers/response.py
"""Immutable response model for AI providers.

All fields are read‑only; the dataclass is frozen to guarantee immutability.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class AIResponse:
    """Container for data returned by an AI provider.

    Attributes
    ----------
    status: str
        Result status, e.g., "success" or "error".
    provider: str
        Identifier of the provider that generated the response.
    metadata: Mapping[str, Any]
        Provider‑specific metadata (e.g., model version).
    usage: Mapping[str, Any]
        Token/compute usage details.
    output: Any
        The actual output payload (e.g., generated text).
    diagnostics: Optional[Mapping[str, Any]]
        Optional diagnostic information for debugging.
    """

    status: str
    provider: str
    metadata: Mapping[str, Any]
    usage: Mapping[str, Any]
    output: Any
    diagnostics: Optional[Mapping[str, Any]] = None
