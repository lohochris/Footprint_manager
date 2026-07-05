from backend.shared.events.bus import DomainEventBus
from .routing_service import EventRoutingService
from datetime import datetime

class IntegrationEventSubscribers:
    def __init__(self, bus: DomainEventBus):
        self.bus = bus
        self._register_subscribers()

    def _register_subscribers(self):
        for event_name in [
            "investigation.created",
            "evidence.uploaded",
            "identity.resolved",
            "collaboration.task.assigned"
        ]:
            self.bus.subscribe(event_name, self.handle_domain_event)

    def handle_domain_event(self, **kwargs):
        tenant_id = kwargs.get("tenant_id")
        event_type = kwargs.get("event_type", "unknown_event")
        payload = kwargs.get("payload", {})

        if not tenant_id:
            return

        timestamp = datetime.utcnow().isoformat()
        idempotency_key = f"{event_type}_{timestamp}"
        EventRoutingService.route_outbound_event(
            tenant_id=tenant_id,
            event_type=event_type,
            payload=payload,
            idempotency_key=idempotency_key
        )
