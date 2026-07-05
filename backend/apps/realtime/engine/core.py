import uuid
from typing import Dict, Any, Optional
from .delivery import DeliveryEngine
from .authorization import ChannelAuthorization
from ..selectors import ChannelSelector

class RealtimeEngine:
    """
    Central coordinator for real-time operations.
    Delegates strictly to specialized engine components.
    """

    @staticmethod
    def process_outbound_event(tenant_id: uuid.UUID, channel_type: str, resource_identifier: str, event_type: str, payload: Dict[str, Any], idempotency_key: Optional[str] = None) -> None:
        """
        1. Resolves the channel.
        2. Dispatches to DeliveryEngine for fan-out.
        """
        channel = ChannelSelector.get_by_resource(tenant_id, channel_type, resource_identifier)
        if not channel:
            return # No channel to deliver to

        DeliveryEngine.deliver_event(
            tenant_id=tenant_id,
            channel_id=channel.id,
            event_type=event_type,
            payload=payload,
            idempotency_key=idempotency_key
        )
