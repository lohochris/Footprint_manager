from backend.shared.events.bus import DomainEventBus
from .stream_service import StreamService
from datetime import datetime

class RealtimeEventSubscribers:
    def __init__(self, bus: DomainEventBus):
        self.bus = bus
        self._register_subscribers()

    def _register_subscribers(self):
        # We listen to key events and fan them out via realtime channels
        for event_name in [
            "investigation.created",
            "evidence.uploaded",
            "identity.resolved",
            "workflow.started",
            "workflow.completed",
            "graph.expanded",
            "risk_score.updated",
            "ai_report.generated",
            "task.assigned",
            "comment.created",
            "notification.created",
            "integration.completed"
        ]:
            self.bus.subscribe(event_name, self.handle_domain_event)

    def handle_domain_event(self, **kwargs):
        tenant_id = kwargs.get("tenant_id")
        event_type = kwargs.get("event_type", "unknown_event")
        payload = kwargs.get("payload", {})

        if not tenant_id:
            return

        # Determine the channel type and resource identifier from the event.
        # This mapping depends heavily on the event payload structure.
        # As a stub for Sprint 14, we will assume all events route to a generic "system" channel.
        # In reality, "investigation.created" might route to the 'organization' channel,
        # "evidence.uploaded" routes to the 'investigation' channel, etc.

        channel_type = "system"
        resource_identifier = "all"

        if "investigation_id" in payload:
            channel_type = "investigation"
            resource_identifier = str(payload["investigation_id"])

        timestamp = datetime.utcnow().isoformat()
        idempotency_key = f"rt_{event_type}_{timestamp}"

        StreamService.publish_event(
            tenant_id=tenant_id,
            channel_type=channel_type,
            resource_identifier=resource_identifier,
            event_type=event_type,
            payload=payload,
            idempotency_key=idempotency_key
        )
