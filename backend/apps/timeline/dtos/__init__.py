from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class TimelineEventDTO:
    id: UUID
    event_type: str
    source_bounded_context: str
    timestamp: datetime
    actor_id: Optional[UUID]
    resource_type: str
    resource_id: UUID
    payload: Dict[str, Any]
    event_version: int
    schema_version: str
    producer: str
    trace_id: str
    correlation_id: str
    causation_id: str


@dataclass
class TimelineDTO:
    id: UUID
    name: str
    description: str
    target_type: str
    target_id: UUID
    events: List[TimelineEventDTO]


@dataclass
class EventSequenceDTO:
    id: UUID
    name: str
    sequence_type: str
    items: List[Dict[str, Any]]  # Representation of EventSequenceItem


@dataclass
class EventClusterDTO:
    id: UUID
    name: str
    description: str
    cluster_type: str
    events: List[TimelineEventDTO]


@dataclass
class TimelineSnapshotDTO:
    id: UUID
    timeline_id: UUID
    timestamp: datetime
    state_payload: Dict[str, Any]
    last_event_applied_id: Optional[UUID]


@dataclass
class TimelineAuditDTO:
    id: UUID
    operation_type: str
    timeline_id: Optional[UUID]
    actor_id: Optional[UUID]
    timestamp: datetime
    details: Dict[str, Any]
    ip_address: Optional[str]
