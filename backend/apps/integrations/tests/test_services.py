import pytest
import uuid
from backend.apps.integrations.services.integration_service import IntegrationService
from backend.apps.integrations.models.integration import Integration

@pytest.mark.django_db
class TestIntegrationService:
    def test_create_integration(self):
        tenant_id = uuid.uuid4()
        dto = IntegrationService.create_integration(
            tenant_id=tenant_id,
            name="Test Splunk",
            provider="rest"
        )
        assert dto.name == "Test Splunk"
        assert dto.provider == "rest"

        integration = Integration.objects.get(id=dto.id)
        assert integration.tenant_id == tenant_id
