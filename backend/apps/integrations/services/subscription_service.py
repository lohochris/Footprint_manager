import uuid
from .dto import SubscriptionDTO
from ..repositories import SubscriptionRepository
from ..models import Subscription

class SubscriptionService:
    @staticmethod
    def create_subscription(tenant_id: uuid.UUID, integration_id: uuid.UUID, event_name: str) -> SubscriptionDTO:
        sub = SubscriptionRepository.create(tenant_id=tenant_id, integration_id=integration_id, event_name=event_name)
        return SubscriptionDTO(
            id=sub.id,
            integration_id=sub.integration_id,
            event_name=sub.event_name,
            is_active=sub.is_active
        )
