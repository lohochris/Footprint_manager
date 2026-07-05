import uuid
from typing import Optional, Dict, Any
from .dto import IntegrationDTO
from ..repositories import IntegrationRepository
from ..selectors import IntegrationSelector
from ..models import Integration

class IntegrationService:
    @staticmethod
    def create_integration(tenant_id: uuid.UUID, name: str, provider: str, configuration: Optional[Dict[str, Any]] = None) -> IntegrationDTO:
        integration = IntegrationRepository.create(
            tenant_id=tenant_id,
            name=name,
            provider=provider,
            configuration=configuration or {}
        )
        return IntegrationService._to_dto(integration)

    @staticmethod
    def get_integration(tenant_id: uuid.UUID, integration_id: uuid.UUID) -> Optional[IntegrationDTO]:
        integration = IntegrationSelector.get_by_id(tenant_id, integration_id)
        if integration:
            return IntegrationService._to_dto(integration)
        return None

    @staticmethod
    def _to_dto(integration: Integration) -> IntegrationDTO:
        return IntegrationDTO(
            id=integration.id,
            tenant_id=integration.tenant_id,
            name=integration.name,
            provider=integration.provider,
            status=integration.status,
            is_enabled=integration.is_enabled,
            configuration=integration.configuration
        )
