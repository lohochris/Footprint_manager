from backend.shared.events.bus import DomainEventBus
from backend.shared.events import BaseDomainEvent
from .metrics import MetricsService

class ObservabilityEventSubscribers:
    """
    Subscribes to global domain events to generate metrics and traces without
    modifying originating bounded contexts.
    """

    @staticmethod
    def handle_event(event: BaseDomainEvent) -> None:
        tenant_id_str = event.metadata.get("tenant_id")
        if not tenant_id_str:
            return

        import uuid
        tenant_id = uuid.UUID(str(tenant_id_str))

        # Generate metrics based on event type
        if event.event_type == "investigation.created":
            MetricsService.capture_metric(tenant_id, "investigations_created", 1.0, source="events")
        elif event.event_type == "evidence.uploaded":
            MetricsService.capture_metric(tenant_id, "evidence_uploaded", 1.0, source="events")
        elif event.event_type == "workflow.completed":
            MetricsService.capture_metric(tenant_id, "workflows_completed", 1.0, source="events")
        elif event.event_type == "integration.completed":
            MetricsService.capture_metric(tenant_id, "integrations_completed", 1.0, source="events")
        elif event.event_type == "integration.failed":
            MetricsService.capture_metric(tenant_id, "integrations_failed", 1.0, source="events")
        elif event.event_type == "ai.request.completed":
            tokens = event.metadata.get("tokens_used", 1)
            MetricsService.capture_metric(tenant_id, "ai_tokens_used", float(tokens), source="events")

    @classmethod
    def register(cls) -> None:
        DomainEventBus.subscribe("investigation.created", cls.handle_event)
        DomainEventBus.subscribe("evidence.uploaded", cls.handle_event)
        DomainEventBus.subscribe("workflow.completed", cls.handle_event)
        DomainEventBus.subscribe("integration.completed", cls.handle_event)
        DomainEventBus.subscribe("integration.failed", cls.handle_event)
        DomainEventBus.subscribe("ai.request.completed", cls.handle_event)
