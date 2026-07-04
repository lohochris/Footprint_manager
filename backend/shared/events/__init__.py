"""
Domain event primitives for Footprint Manager.

This module provides the foundational base class for all domain events
in the platform.  Domain events represent facts that have occurred within
the system.  They are immutable, timestamped, and carry a unique identity.

Naming convention: events are named in the past tense (e.g.
``UserRegistered``, ``InvestigationCreated``).

Usage::

    from backend.shared.events import BaseDomainEvent
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class UserRegistered(BaseDomainEvent):
        user_id: str
        email: str
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar


@dataclass(frozen=True)
class BaseDomainEvent:
    """
    Immutable base class for all Footprint Manager domain events.

    Subclasses must be frozen dataclasses.  All fields added by subclasses
    should represent the minimal state required to describe what happened.

    Attributes:
        event_id: Globally unique identifier for this event instance.
        event_type: Dotted-namespace string identifying the event type
            (e.g. ``"accounts.user.registered"``).  Derived automatically
            from the class name if not overridden.
        occurred_at: UTC timestamp recording when the event occurred.
        aggregate_id: UUID of the aggregate root that emitted this event.
        aggregate_type: Name of the aggregate type (e.g. ``"User"``).
        version: Schema version for forward-compatibility.
        metadata: Arbitrary key-value bag for tracing context (request_id,
            correlation_id, tenant_id, actor_id).
    """

    #: Subclasses should set this to a fixed dotted string.
    event_type: ClassVar[str] = "base.domain.event"

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    aggregate_id: uuid.UUID | None = field(default=None)
    aggregate_type: str | None = field(default=None)
    version: int = field(default=1)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialise the event to a plain dictionary suitable for JSON encoding.

        Returns:
            Dictionary representation of the event including all fields and
            the ``event_type`` class variable.
        """
        return {
            "event_id": str(self.event_id),
            "event_type": self.__class__.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": str(self.aggregate_id) if self.aggregate_id else None,
            "aggregate_type": self.aggregate_type,
            "version": self.version,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"event_id={self.event_id!r}, "
            f"occurred_at={self.occurred_at.isoformat()!r})"
        )


__all__ = ["BaseDomainEvent"]
