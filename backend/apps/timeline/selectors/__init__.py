from datetime import datetime
from typing import List, Optional
from uuid import UUID

from django.db.models import QuerySet

from ..models import EventCluster, Timeline, TimelineEvent, TimelineSnapshot


class TimelineQuery:
    """Reusable abstraction for querying timelines."""
    
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id
        self.queryset = TimelineEvent.objects.filter(workspace_id=tenant_id)

    def by_resource(self, resource_type: str, resource_id: UUID) -> "TimelineQuery":
        self.queryset = self.queryset.filter(resource_type=resource_type, resource_id=resource_id)
        return self

    def by_investigation(self, investigation_id: UUID) -> "TimelineQuery":
        # Assumes investigation events have a correlation_id matching investigation_id
        self.queryset = self.queryset.filter(correlation_id=str(investigation_id))
        return self

    def between_dates(self, start_time: datetime, end_time: datetime) -> "TimelineQuery":
        self.queryset = self.queryset.filter(timestamp__range=(start_time, end_time))
        return self

    def before_timestamp(self, timestamp: datetime) -> "TimelineQuery":
        self.queryset = self.queryset.filter(timestamp__lte=timestamp)
        return self

    def by_event_type(self, event_type: str) -> "TimelineQuery":
        self.queryset = self.queryset.filter(event_type=event_type)
        return self

    def by_actor(self, actor_id: UUID) -> "TimelineQuery":
        self.queryset = self.queryset.filter(actor_id=actor_id)
        return self

    def resolve(self) -> QuerySet[TimelineEvent]:
        return self.queryset.order_by("timestamp")


def get_timeline_events(tenant_id: UUID, **kwargs) -> QuerySet[TimelineEvent]:
    query = TimelineQuery(tenant_id)
    if "resource_type" in kwargs and "resource_id" in kwargs:
        query.by_resource(kwargs["resource_type"], kwargs["resource_id"])
    if "investigation_id" in kwargs:
        query.by_investigation(kwargs["investigation_id"])
    if "start_time" in kwargs and "end_time" in kwargs:
        query.between_dates(kwargs["start_time"], kwargs["end_time"])
    if "actor_id" in kwargs:
        query.by_actor(kwargs["actor_id"])
    return query.resolve()


def get_timeline_for_target(target_type: str, target_id: UUID, tenant_id: UUID) -> Optional[Timeline]:
    return Timeline.objects.filter(
        target_type=target_type,
        target_id=target_id,
        workspace_id=tenant_id,
    ).first()


def get_event_clusters_for_resource(resource_type: str, resource_id: UUID, tenant_id: UUID) -> QuerySet[EventCluster]:
    return EventCluster.objects.filter(
        events__resource_type=resource_type,
        events__resource_id=resource_id,
        workspace_id=tenant_id,
    ).distinct()


def get_latest_snapshot_before(timeline_id: UUID, timestamp: datetime, tenant_id: UUID) -> Optional[TimelineSnapshot]:
    return TimelineSnapshot.objects.filter(
        timeline_id=timeline_id,
        timestamp__lte=timestamp,
        workspace_id=tenant_id,
    ).order_by("-timestamp").first()

__all__ = [
    "TimelineQuery",
    "get_timeline_events",
    "get_timeline_for_target",
    "get_event_clusters_for_resource",
    "get_latest_snapshot_before",
]
