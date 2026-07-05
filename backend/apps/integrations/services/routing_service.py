import uuid
from typing import Dict, Any
from ..engine.core import IntegrationEngine

class EventRoutingService:
    @staticmethod
    def route_outbound_event(tenant_id: uuid.UUID, event_type: str, payload: Dict[str, Any], idempotency_key: str):
        engine = IntegrationEngine()
        engine.process_outbound_event(tenant_id, event_type, payload, idempotency_key)

    @staticmethod
    def handle_inbound_webhook(tenant_id: uuid.UUID, integration_id: uuid.UUID, payload: Dict[str, Any], idempotency_key: str):
        engine = IntegrationEngine()
        engine.process_inbound_event(tenant_id, integration_id, payload, idempotency_key)

        # Translating external events into domain events through the shared event bus
        from backend.shared.events.bus import DomainEventBus
        bus = DomainEventBus()
        bus.publish("integration.inbound_webhook_received", payload=payload, tenant_id=tenant_id)
