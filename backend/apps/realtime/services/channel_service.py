import uuid
from typing import List, Optional
from ..repositories import ChannelRepository
from ..selectors import ChannelSelector
from .dto import ChannelDTO

class ChannelService:
    @staticmethod
    def get_or_create_channel(tenant_id: uuid.UUID, channel_type: str, resource_identifier: str, permissions_required: Optional[List[str]] = None) -> ChannelDTO:
        channel = ChannelSelector.get_by_resource(tenant_id, channel_type, resource_identifier)
        if not channel:
            channel = ChannelRepository.create(tenant_id, channel_type, resource_identifier, permissions_required)

        return ChannelDTO(
            id=channel.id,
            tenant_id=channel.tenant_id,
            channel_type=channel.channel_type,
            resource_identifier=channel.resource_identifier,
            permissions_required=channel.permissions_required
        )
