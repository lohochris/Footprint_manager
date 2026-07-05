from typing import Any, Dict
from uuid import UUID

from backend.shared.event_bus import event_bus

from ..repositories import EventRepository, TimelineRepository
from ..services import TimelineService

# In a real app these would be instantiated via DI container.
timeline_service = TimelineService(
    repository=TimelineRepository(),
    event_repository=EventRepository(),
)

EVENTS_TO_SUBSCRIBE = [
    "InvestigationCreated",
    "InvestigationClosed",
    "EvidenceUploaded",
    "IdentityResolved",
    "GraphExpanded",
    "RiskScoreCalculated",
    "AIReportGenerated",
    "WorkflowStarted",
    "WorkflowCompleted",
    "DecisionGenerated",
    "RecommendationGenerated",
    "ApprovalCompleted",
    "ComplianceViolation",
    "IntegrationCompleted",
]

def handle_platform_event(event_type: str, payload: Dict[str, Any]) -> None:
    """Generic handler for recording platform events into the Timeline."""
    # Assuming standard payload structure across the platform events
    tenant_id = payload.get("tenant_id")
    organization_id = payload.get("organization_id")
    resource_type = payload.get("resource_type", "Unknown")
    resource_id_str = payload.get("resource_id")
    
    if not tenant_id or not organization_id or not resource_id_str:
        return

    resource_id = UUID(resource_id_str)
    
    timeline_service.record_event(
        event_type=event_type,
        source_bounded_context=payload.get("source_context", "Unknown"),
        resource_type=resource_type,
        resource_id=resource_id,
        payload=payload,
        tenant_id=UUID(tenant_id),
        organization_id=UUID(organization_id),
        actor_id=UUID(payload["actor_id"]) if payload.get("actor_id") else None,
        event_version=payload.get("event_version", 1),
        schema_version=payload.get("schema_version", "1.0.0"),
        producer=payload.get("producer", ""),
        trace_id=payload.get("trace_id", ""),
        correlation_id=payload.get("correlation_id", ""),
        causation_id=payload.get("causation_id", ""),
    )

for event_name in EVENTS_TO_SUBSCRIBE:
    @event_bus.subscribe(event_name)
    def create_handler(payload: Dict[str, Any], event_name=event_name) -> None:
        handle_platform_event(event_name, payload)
