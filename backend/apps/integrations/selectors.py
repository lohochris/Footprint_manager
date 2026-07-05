import uuid
from typing import Optional
from django.db.models import QuerySet
from .models import Integration, IntegrationEndpoint, IntegrationEvent, DeliveryAttempt, Subscription, IntegrationAudit

class IntegrationSelector:
    @staticmethod
    def get_by_id(tenant_id: uuid.UUID, integration_id: uuid.UUID) -> Optional[Integration]:
        return Integration.objects.filter(tenant_id=tenant_id, id=integration_id).first()

    @staticmethod
    def list_active(tenant_id: uuid.UUID) -> QuerySet[Integration]:
        return Integration.objects.filter(tenant_id=tenant_id, status=Integration.Status.ACTIVE, is_enabled=True)

class SubscriptionSelector:
    @staticmethod
    def list_by_event(tenant_id: uuid.UUID, event_name: str) -> QuerySet[Subscription]:
        return Subscription.objects.filter(tenant_id=tenant_id, event_name=event_name, is_active=True).select_related('integration')

class EventSelector:
    @staticmethod
    def get_by_idempotency_key(tenant_id: uuid.UUID, idempotency_key: str) -> Optional[IntegrationEvent]:
        return IntegrationEvent.objects.filter(tenant_id=tenant_id, idempotency_key=idempotency_key).first()

    @staticmethod
    def list_pending(tenant_id: uuid.UUID) -> QuerySet[IntegrationEvent]:
        return IntegrationEvent.objects.filter(tenant_id=tenant_id, status=IntegrationEvent.Status.PENDING)

class AuditSelector:
    @staticmethod
    def list_by_integration(tenant_id: uuid.UUID, integration_id: uuid.UUID) -> QuerySet[IntegrationAudit]:
        return IntegrationAudit.objects.filter(tenant_id=tenant_id, integration_id=integration_id).order_by('-created_at')
