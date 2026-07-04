# backend/apps/osint/events/__init__.py
"""OSINT Discovery domain events.

All events are immutable frozen dataclasses that extend
``backend.shared.events.BaseDomainEvent``.  They follow the naming
convention established in the platform events module: past-tense names
(e.g. ``DiscoveryJobQueued``, ``DiscoveryJobCompleted``).

Event types use the dotted namespace ``"osint.discovery_job.*"`` and
``"osint.discovery_result.*"``.

These are currently placeholder interfaces — they are emittable and
serialisable via ``to_dict()`` inherited from ``BaseDomainEvent``, but
no dispatcher or bus integration is wired in Sprint 6.  The event
contracts are defined now to allow downstream sprints (notifications,
analytics, graph processing) to subscribe without requiring model
changes.

Usage::

    from backend.apps.osint.events import DiscoveryJobCompleted
    import uuid
    from datetime import datetime, UTC

    event = DiscoveryJobCompleted(
        aggregate_id=job.id,
        aggregate_type="DiscoveryJob",
        job_id=job.id,
        completed_at=datetime.now(tz=UTC),
        duration_ms=1234,
        result_count=3,
    )
    print(event.to_dict())
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from backend.shared.events import BaseDomainEvent


# ---------------------------------------------------------------------------
# Job lifecycle events
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DiscoveryJobQueued(BaseDomainEvent):
    """Raised when a DiscoveryJob is created and placed in the queue.

    Attributes
    ----------
    job_id:
        UUID of the newly created ``DiscoveryJob``.
    provider_name:
        Slug of the assigned ``DiscoveryProvider``.
    triggered_by:
        ``DiscoveryJobTrigger`` value string describing the initiating
        mechanism (manual / scheduled / webhook / api).
    """

    event_type: ClassVar[str] = "osint.discovery_job.queued"

    job_id: uuid.UUID = field(default_factory=uuid.uuid4)
    provider_name: str = ""
    triggered_by: str = ""

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            {
                "job_id": str(self.job_id),
                "provider_name": self.provider_name,
                "triggered_by": self.triggered_by,
            }
        )
        return base


@dataclass(frozen=True)
class DiscoveryJobStarted(BaseDomainEvent):
    """Raised when a DiscoveryJob transitions from queued to running.

    Attributes
    ----------
    job_id:
        UUID of the ``DiscoveryJob`` now running.
    started_at:
        UTC datetime when execution began.
    """

    event_type: ClassVar[str] = "osint.discovery_job.started"

    job_id: uuid.UUID = field(default_factory=uuid.uuid4)
    started_at: datetime | None = None

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            {
                "job_id": str(self.job_id),
                "started_at": self.started_at.isoformat() if self.started_at else None,
            }
        )
        return base


@dataclass(frozen=True)
class DiscoveryJobCompleted(BaseDomainEvent):
    """Raised when a DiscoveryJob reaches the ``completed`` terminal state.

    Attributes
    ----------
    job_id:
        UUID of the completed ``DiscoveryJob``.
    completed_at:
        UTC datetime when the job completed.
    duration_ms:
        Wall-clock milliseconds of execution.
    result_count:
        Number of ``DiscoveryResult`` rows persisted.
    """

    event_type: ClassVar[str] = "osint.discovery_job.completed"

    job_id: uuid.UUID = field(default_factory=uuid.uuid4)
    completed_at: datetime | None = None
    duration_ms: int = 0
    result_count: int = 0

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            {
                "job_id": str(self.job_id),
                "completed_at": self.completed_at.isoformat() if self.completed_at else None,
                "duration_ms": self.duration_ms,
                "result_count": self.result_count,
            }
        )
        return base


@dataclass(frozen=True)
class DiscoveryJobFailed(BaseDomainEvent):
    """Raised when a DiscoveryJob reaches the ``failed`` terminal state.

    Attributes
    ----------
    job_id:
        UUID of the failed ``DiscoveryJob``.
    failure_reason:
        Human-readable description of the error.
    retry_count:
        Number of retry attempts made (including the failing attempt).
    """

    event_type: ClassVar[str] = "osint.discovery_job.failed"

    job_id: uuid.UUID = field(default_factory=uuid.uuid4)
    failure_reason: str = ""
    retry_count: int = 0

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            {
                "job_id": str(self.job_id),
                "failure_reason": self.failure_reason,
                "retry_count": self.retry_count,
            }
        )
        return base


# ---------------------------------------------------------------------------
# Result events
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DiscoveryResultCreated(BaseDomainEvent):
    """Raised when a DiscoveryResult is persisted after provider execution.

    Attributes
    ----------
    result_id:
        UUID of the newly created ``DiscoveryResult``.
    job_id:
        UUID of the parent ``DiscoveryJob``.
    result_type:
        ``DiscoveryResultType`` value string.
    confidence:
        Decimal confidence score serialised as a string to maintain
        precision across JSON serialisation.
    """

    event_type: ClassVar[str] = "osint.discovery_result.created"

    result_id: uuid.UUID = field(default_factory=uuid.uuid4)
    job_id: uuid.UUID = field(default_factory=uuid.uuid4)
    result_type: str = ""
    confidence: str = "1.0000"  # Decimal serialised as str

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(
            {
                "result_id": str(self.result_id),
                "job_id": str(self.job_id),
                "result_type": self.result_type,
                "confidence": self.confidence,
            }
        )
        return base


__all__ = [
    "DiscoveryJobQueued",
    "DiscoveryJobStarted",
    "DiscoveryJobCompleted",
    "DiscoveryJobFailed",
    "DiscoveryResultCreated",
]
