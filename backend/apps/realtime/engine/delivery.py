import uuid
from typing import Dict, Any, Optional, List
from ..models.subscription import Subscription
from ..providers.registry import ProviderRegistry
from ..selectors import SubscriptionSelector

class DeliveryEngine:
    @staticmethod
    def deliver_event(tenant_id: uuid.UUID, channel_id: uuid.UUID, event_type: str, payload: Dict[str, Any], _idempotency_key: Optional[str] = None) -> None:
        """
        Fans out the event to all active subscriptions on the channel.
        Delegates protocol-specific sending to the ProviderRegistry.
        """
        subscriptions = SubscriptionSelector.get_active_subscribers(tenant_id, channel_id)

        # Group by protocol
        protocol_subs: Dict[str, List[Subscription]] = {}
        for sub in subscriptions:
            protocol = sub.connection.protocol
            if protocol not in protocol_subs:
                protocol_subs[protocol] = []
            protocol_subs[protocol].append(sub)

        for protocol, subs in protocol_subs.items():
            provider = ProviderRegistry.get_provider(protocol)
            for sub in subs:
                # We could broadcast if the provider supports channel grouping,
                # but we'll send point-to-point here to manage backpressure/auditing per connection
                provider.send_to_connection(sub.connection.session_id, event_type, payload)
