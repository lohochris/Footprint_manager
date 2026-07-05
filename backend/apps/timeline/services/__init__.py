from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.db import transaction

from ..models import Timeline, TimelineAudit, TimelineEvent, TimelineSnapshot
from ..repositories import AuditRepository, EventRepository, SnapshotRepository, TimelineRepository


class TimelineService:
    def __init__(self, repository: TimelineRepository, event_repository: EventRepository):
        self.repository = repository
        self.event_repository = event_repository

    @transaction.atomic
    def record_event(
        self,
        event_type: str,
        source_bounded_context: str,
        resource_type: str,
        resource_id: UUID,
        payload: Dict[str, Any],
        tenant_id: UUID,
        organization_id: UUID,
        actor_id: Optional[UUID] = None,
        event_version: int = 1,
        schema_version: str = "1.0.0",
        producer: str = "",
        trace_id: str = "",
        correlation_id: str = "",
        causation_id: str = "",
    ) -> TimelineEvent:
        event = self.event_repository.create_event(
            event_type=event_type,
            source_bounded_context=source_bounded_context,
            timestamp=datetime.now(),
            resource_type=resource_type,
            resource_id=resource_id,
            payload=payload,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            event_version=event_version,
            schema_version=schema_version,
            producer=producer,
            trace_id=trace_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )

        # Automatically associate event with the target's timeline
        timeline = self.repository.get_or_create_timeline(
            name=f"{resource_type} Timeline",
            target_type=resource_type,
            target_id=resource_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
        )
        timeline.events.add(event)

        # If it's part of an investigation, also link to the investigation timeline
        if correlation_id:
            try:
                inv_id = UUID(correlation_id)
                inv_timeline = self.repository.get_or_create_timeline(
                    name="Investigation Timeline",
                    target_type="Investigation",
                    target_id=inv_id,
                    tenant_id=tenant_id,
                    organization_id=organization_id,
                )
                inv_timeline.events.add(event)
            except ValueError:
                pass

        return event


class PlaybackService:
    def __init__(self, snapshot_repository: SnapshotRepository, audit_repository: AuditRepository):
        self.snapshot_repository = snapshot_repository
        self.audit_repository = audit_repository

    def generate_snapshot(
        self, timeline: Timeline, timestamp: datetime, tenant_id: UUID, organization_id: UUID, user_id: UUID
    ) -> TimelineSnapshot:
        # Implementation to reconstruct state by replaying events up to the timestamp
        state_payload = {}  # Reconstructed state
        last_event = timeline.events.filter(timestamp__lte=timestamp).order_by("-timestamp").first()

        snapshot = self.snapshot_repository.create_snapshot(
            timeline=timeline,
            timestamp=timestamp,
            state_payload=state_payload,
            last_event_applied=last_event,
            tenant_id=tenant_id,
            organization_id=organization_id,
        )

        self.audit_repository.log_operation(
            operation_type=TimelineAudit.OperationType.SNAPSHOT,
            actor_id=user_id,
            details={"timestamp": timestamp.isoformat(), "snapshot_id": str(snapshot.id)},
            tenant_id=tenant_id,
            organization_id=organization_id,
            timeline=timeline,
        )

        return snapshot

    def replay_timeline(self, timeline: Timeline, end_timestamp: datetime, user_id: UUID, tenant_id: UUID, organization_id: UUID) -> List[TimelineEvent]:
        # This is for authorized historical playback
        self.audit_repository.log_operation(
            operation_type=TimelineAudit.OperationType.REPLAY,
            actor_id=user_id,
            details={"end_timestamp": end_timestamp.isoformat()},
            tenant_id=tenant_id,
            organization_id=organization_id,
            timeline=timeline,
        )
        return list(timeline.events.filter(timestamp__lte=end_timestamp).order_by("timestamp"))

__all__ = [
    "TimelineService",
    "PlaybackService",
]
