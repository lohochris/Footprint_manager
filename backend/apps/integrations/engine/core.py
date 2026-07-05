import uuid
from typing import Dict, Any, List
from .transformation import PayloadTransformer
from .delivery_executor import DeliveryExecutor
from ..selectors import SubscriptionSelector, EventSelector
from ..repositories import EventRepository, AuditRepository

class IntegrationEngine:
    def __init__(self):
        self.transformer = PayloadTransformer()
        self.delivery_executor = DeliveryExecutor()

    def process_outbound_event(self, tenant_id: uuid.UUID, event_type: str, payload: Dict[str, Any], idempotency_key: str):
        """
        Coordinates the flow: find subscriptions -> transform payload -> deliver.
        """
        subscriptions = SubscriptionSelector.list_by_event(tenant_id, event_type)
        if not subscriptions.exists():
            return

        transformed_payload = self.transformer.to_provider_format(event_type, payload)

        for sub in subscriptions:
            integration = sub.integration
            for endpoint in integration.endpoints.all():
                # Avoid duplicates
                unique_key = f"{idempotency_key}_{endpoint.id}"
                if EventSelector.get_by_idempotency_key(tenant_id, unique_key):
                    continue

                event = EventRepository.create(
                    tenant_id=tenant_id,
                    integration_id=integration.id,
                    direction='outbound',
                    event_type=event_type,
                    payload=payload,
                    idempotency_key=unique_key,
                    endpoint_id=endpoint.id
                )

                success = self.delivery_executor.execute_delivery(tenant_id, event, endpoint, transformed_payload)

                final_status = 'delivered' if success else 'failed'
                EventRepository.update_status(tenant_id, event.id, final_status)

                AuditRepository.append(
                    tenant_id=tenant_id,
                    integration_id=integration.id,
                    action=f"Deliver Outbound {event_type}",
                    status=final_status,
                    payload_hash=unique_key # mock hash
                )

    def process_inbound_event(self, tenant_id: uuid.UUID, integration_id: uuid.UUID, payload: Dict[str, Any], idempotency_key: str):
        """
        Handles webhooks or messages received from an external provider, storing it.
        """
        if EventSelector.get_by_idempotency_key(tenant_id, idempotency_key):
            return

        EventRepository.create(
            tenant_id=tenant_id,
            integration_id=integration_id,
            direction='inbound',
            event_type='ExternalWebhookReceived',
            payload=payload,
            idempotency_key=idempotency_key,
            status='delivered'
        )

        AuditRepository.append(
            tenant_id=tenant_id,
            integration_id=integration_id,
            action="Receive Inbound Webhook",
            status="delivered",
            payload_hash=idempotency_key
        )
