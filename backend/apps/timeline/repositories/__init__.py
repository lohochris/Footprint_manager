from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from ..models import (
    EventCluster,
    Timeline,
    TimelineAudit,
    TimelineEvent,
    TimelineSnapshot,
)


class EventRepository:
    def create_event(
        self,
        event_type: str,
        source_bounded_context: str,
        timestamp: Any,
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
        return TimelineEvent.objects.create(
            event_type=event_type,
            source_bounded_context=source_bounded_context,
            timestamp=timestamp,
            resource_type=resource_type,
            resource_id=resource_id,
            payload=payload,
            workspace_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            event_version=event_version,
            schema_version=schema_version,
            producer=producer,
            trace_id=trace_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )

    def get_event(self, event_id: UUID, tenant_id: UUID) -> Optional[TimelineEvent]:
        try:
            return TimelineEvent.objects.get(id=event_id, workspace_id=tenant_id)
        except ObjectDoesNotExist:
            return None


class TimelineRepository:
    def get_or_create_timeline(
        self,
        name: str,
        target_type: str,
        target_id: UUID,
        tenant_id: UUID,
        organization_id: UUID,
    ) -> Timeline:
        timeline, _ = Timeline.objects.get_or_create(
            target_type=target_type,
            target_id=target_id,
            workspace_id=tenant_id,
            defaults={
                "name": name,
                "organization_id": organization_id,
            },
        )
        return timeline


class ClusterRepository:
    def create_cluster(
        self,
        name: str,
        cluster_type: str,
        events: List[TimelineEvent],
        tenant_id: UUID,
        organization_id: UUID,
    ) -> EventCluster:
        cluster = EventCluster.objects.create(
            name=name,
            cluster_type=cluster_type,
            workspace_id=tenant_id,
            organization_id=organization_id,
        )
        cluster.events.set(events)
        return cluster


class SnapshotRepository:
    def create_snapshot(
        self,
        timeline: Timeline,
        timestamp: Any,
        state_payload: Dict[str, Any],
        last_event_applied: Optional[TimelineEvent],
        tenant_id: UUID,
        organization_id: UUID,
    ) -> TimelineSnapshot:
        return TimelineSnapshot.objects.create(
            timeline=timeline,
            timestamp=timestamp,
            state_payload=state_payload,
            last_event_applied=last_event_applied,
            workspace_id=tenant_id,
            organization_id=organization_id,
        )


class AuditRepository:
    def log_operation(
        self,
        operation_type: str,
        actor_id: Optional[UUID],
        details: Dict[str, Any],
        tenant_id: UUID,
        organization_id: UUID,
        timeline: Optional[Timeline] = None,
        ip_address: Optional[str] = None,
    ) -> TimelineAudit:
        return TimelineAudit.objects.create(
            operation_type=operation_type,
            actor_id=actor_id,
            details=details,
            workspace_id=tenant_id,
            organization_id=organization_id,
            timeline=timeline,
            ip_address=ip_address,
        )

__all__ = [
    "EventRepository",
    "TimelineRepository",
    "ClusterRepository",
    "SnapshotRepository",
    "AuditRepository",
]
