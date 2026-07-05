import pytest
import uuid
from django.contrib.auth import get_user_model
from backend.apps.realtime.services.channel_service import ChannelService
from backend.apps.realtime.models.channel import RealtimeChannel

User = get_user_model()

@pytest.mark.django_db
class TestRealtimeServices:
    def test_get_or_create_channel(self):
        tenant_id = uuid.uuid4()
        dto = ChannelService.get_or_create_channel(
            tenant_id=tenant_id,
            channel_type="investigation",
            resource_identifier="inv-123"
        )
        assert dto.channel_type == "investigation"
        assert dto.resource_identifier == "inv-123"
        assert dto.tenant_id == tenant_id

        channel = RealtimeChannel.objects.get(id=dto.id)
        assert channel.tenant_id == tenant_id
