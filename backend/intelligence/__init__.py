# Intelligence package

"""Top‑level package for the Intelligence enrichment layer.

The package exposes the execution context, provider states, and policy evaluation
types used throughout the intelligence execution pipeline.
"""

from .context import ExecutionContext
from .provider_state import ProviderLifecycleState
from .policy import PolicyEngine, EvaluationResult

__all__ = [
    "ExecutionContext",
    "ProviderLifecycleState",
    "PolicyEngine",
    "EvaluationResult",
]
