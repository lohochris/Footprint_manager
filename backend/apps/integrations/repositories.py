import uuid
from typing import Optional, Dict, Any, List
from .models import Integration, IntegrationEndpoint, IntegrationEvent, DeliveryAttempt, Subscription, IntegrationAudit

class IntegrationRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, name: str, provider: str, **kwargs) -> Integration:
        return Integration.objects.create(tenant_id=tenant_id, name=name, provider=provider, **kwargs)

    @staticmethod
    def update(tenant_id: uuid.UUID, integration_id: uuid.UUID, **kwargs) -> Optional[Integration]:
        updated = Integration.objects.filter(tenant_id=tenant_id, id=integration_id).update(**kwargs)
        if updated:
            return Integration.objects.get(tenant_id=tenant_id, id=integration_id)
        return None

class EndpointRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, integration_id: uuid.UUID, endpoint_type: str, url: str, **kwargs) -> IntegrationEndpoint:
        return IntegrationEndpoint.objects.create(tenant_id=tenant_id, integration_id=integration_id, endpoint_type=endpoint_type, url=url, **kwargs)

class EventRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, integration_id: uuid.UUID, direction: str, event_type: str, payload: Dict[str, Any], idempotency_key: str, **kwargs) -> IntegrationEvent:
        return IntegrationEvent.objects.create(
            tenant_id=tenant_id,
            integration_id=integration_id,
            direction=direction,
            event_type=event_type,
            payload=payload,
            idempotency_key=idempotency_key,
            **kwargs
        )

    @staticmethod
    def update_status(tenant_id: uuid.UUID, event_id: uuid.UUID, status: str) -> bool:
        return IntegrationEvent.objects.filter(tenant_id=tenant_id, id=event_id).update(status=status) > 0

class DeliveryRepository:
    @staticmethod
    def record_attempt(tenant_id: uuid.UUID, event_id: uuid.UUID, idempotency_key: str, attempt_number: int, **kwargs) -> DeliveryAttempt:
        return DeliveryAttempt.objects.create(
            tenant_id=tenant_id,
            event_id=event_id,
            idempotency_key=idempotency_key,
            attempt_number=attempt_number,
            **kwargs
        )

class SubscriptionRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, integration_id: uuid.UUID, event_name: str, **kwargs) -> Subscription:
        return Subscription.objects.create(tenant_id=tenant_id, integration_id=integration_id, event_name=event_name, **kwargs)

class AuditRepository:
    @staticmethod
    def append(tenant_id: uuid.UUID, integration_id: uuid.UUID, action: str, status: str, **kwargs) -> IntegrationAudit:
        return IntegrationAudit.objects.create(
            tenant_id=tenant_id,
            integration_id=integration_id,
            action=action,
            status=status,
            **kwargs
        )
