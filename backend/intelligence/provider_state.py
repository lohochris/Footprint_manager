"""Provider lifecycle state model."""

from enum import StrEnum

class ProviderLifecycleState(StrEnum):
    INITIALIZED = "initialized"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    TERMINATED = "terminated"
