"""Execution context for intelligence enrichers.

Provides a lightweight immutable container for data passed to and
returned from enrichment stages. It can be extended later with
additional fields as needed.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(frozen=True)
class ExecutionContext:
    """Immutable context passed to intelligence enrichers.

    Attributes
    ----------
    data: Dict[str, Any]
        Arbitrary data payload that enrichers can read and augment.
    metadata: Dict[str, Any]
        Additional metadata produced by enrichers.
    """

    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
