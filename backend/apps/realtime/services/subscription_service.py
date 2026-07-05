import uuid
from ..repositories import SubscriptionRepository
from ..engine.authorization import ChannelAuthorization
from ..selectors import ChannelSelector
from .dto import SubscriptionDTO

class SubscriptionService:
    @staticmethod
    def subscribe(tenant_id: uuid.UUID, user_id: uuid.UUID, channel_id: uuid.UUID, connection_id: uuid.UUID) -> SubscriptionDTO:
        channel = ChannelSelector.get_by_resource(tenant_id, "id", str(channel_id)) # Simplifying lookup for stub
        if channel and not ChannelAuthorization.is_authorized(user_id, channel):
            raise PermissionError("Not authorized to subscribe to this channel")

        sub = SubscriptionRepository.create(tenant_id, user_id, channel_id, connection_id)
        return SubscriptionDTO(
            id=sub.id,
            tenant_id=sub.tenant_id,
            channel_id=sub.channel_id,
            connection_id=sub.connection_id,
            status=sub.status
        )

    @staticmethod
    def unsubscribe(subscription_id: uuid.UUID) -> None:
        SubscriptionRepository.deactivate(subscription_id)
