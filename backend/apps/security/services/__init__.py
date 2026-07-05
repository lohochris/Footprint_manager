from typing import List
from uuid import UUID

from django.db import transaction

from backend.shared.event_bus import event_bus

from ..engine import SecurityEngine
from ..models import APIKey, SecurityEvent
from ..repositories import APIKeyRepository, EventRepository


class APIKeyService:
    def __init__(self, repository: APIKeyRepository, event_repository: EventRepository):
        self.repository = repository
        self.event_repository = event_repository

    @transaction.atomic
    def create_api_key(
        self,
        name: str,
        owner_id: UUID,
        key_hash: str,
        scopes: List[str],
        tenant_id: UUID,
        organization_id: UUID,
    ) -> APIKey:
        
        api_key = self.repository.create_api_key(
            name=name,
            owner_id=owner_id,
            key_hash=key_hash,
            scopes=scopes,
            tenant_id=tenant_id,
            organization_id=organization_id,
        )

        event = self.event_repository.log_event(
            event_type=SecurityEvent.EventType.API_KEY_CREATED,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id=owner_id,
            details={"api_key_id": str(api_key.id), "scopes": scopes},
        )
        
        event_bus.publish(
            "APIKeyCreated",
            {
                "api_key_id": str(api_key.id),
                "owner_id": str(owner_id),
                "tenant_id": str(tenant_id),
                "organization_id": str(organization_id),
            },
        )

        return api_key

    @transaction.atomic
    def revoke_api_key(
        self,
        api_key: APIKey,
        actor_id: UUID,
    ) -> None:
        api_key.status = APIKey.Status.REVOKED
        api_key.save(update_fields=["status"])

        self.event_repository.log_event(
            event_type=SecurityEvent.EventType.API_KEY_REVOKED,
            tenant_id=api_key.workspace_id,
            organization_id=api_key.organization_id,
            actor_id=actor_id,
            details={"api_key_id": str(api_key.id)},
        )
        
        event_bus.publish(
            "APIKeyRevoked",
            {
                "api_key_id": str(api_key.id),
                "tenant_id": str(api_key.workspace_id),
                "organization_id": str(api_key.organization_id),
                "actor_id": str(actor_id),
            },
        )

__all__ = [
    "APIKeyService",
]
