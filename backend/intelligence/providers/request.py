# backend/intelligence/providers/request.py
"""Immutable request model for AI providers.

All fields are read‑only; the dataclass is frozen to guarantee immutability.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class AIRequest:
    """Container for data sent to an AI provider.

    Attributes
    ----------
    task: str
        Logical task name, e.g., "text_generation".
    execution_context: Any
        Reference to the current ExecutionContext (or a serialisable
        representation). Stored as Any to avoid a hard dependency on the
        intelligence package.
    payload: Mapping[str, Any]
        Input data for the provider – typically the prompt or raw content.
    metadata: Mapping[str, Any]
        Additional metadata that may influence the request (e.g., temperature).
    options: Optional[Mapping[str, Any]]
        Provider‑specific optional parameters. May be None.
    """

    task: str
    execution_context: Any
    payload: Mapping[str, Any]
    metadata: Mapping[str, Any]
    options: Optional[Mapping[str, Any]] = None
