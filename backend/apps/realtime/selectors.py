import uuid
from typing import List, Optional
from django.db.models import QuerySet
from .models import RealtimeChannel, Connection, Subscription, StreamEvent, Presence

class ChannelSelector:
    @staticmethod
    def get_by_resource(tenant_id: uuid.UUID, channel_type: str, resource_identifier: str) -> Optional[RealtimeChannel]:
        return RealtimeChannel.objects.filter(
            tenant_id=tenant_id,
            channel_type=channel_type,
            resource_identifier=resource_identifier
        ).first()

    @staticmethod
    def list_for_tenant(tenant_id: uuid.UUID) -> QuerySet[RealtimeChannel]:
        return RealtimeChannel.objects.filter(tenant_id=tenant_id)

class ConnectionSelector:
    @staticmethod
    def get_connection(tenant_id: uuid.UUID, session_id: str) -> Optional[Connection]:
        return Connection.objects.filter(tenant_id=tenant_id, session_id=session_id).first()

    @staticmethod
    def get_active_connections_for_user(tenant_id: uuid.UUID, user_id: uuid.UUID) -> QuerySet[Connection]:
        return Connection.objects.filter(tenant_id=tenant_id, user_id=user_id, state=Connection.State.CONNECTED)

class SubscriptionSelector:
    @staticmethod
    def get_active_subscribers(tenant_id: uuid.UUID, channel_id: uuid.UUID) -> QuerySet[Subscription]:
        return Subscription.objects.filter(
            tenant_id=tenant_id,
            channel_id=channel_id,
            status=Subscription.Status.ACTIVE,
            connection__state=Connection.State.CONNECTED
        ).select_related('connection', 'user')

class StreamEventSelector:
    @staticmethod
    def get_events_since(tenant_id: uuid.UUID, channel_id: uuid.UUID, last_sequence_number: int) -> QuerySet[StreamEvent]:
        """Supports replay feature."""
        return StreamEvent.objects.filter(
            tenant_id=tenant_id,
            channel_id=channel_id,
            sequence_number__gt=last_sequence_number
        ).order_by('sequence_number')

class PresenceSelector:
    @staticmethod
    def get_presence(tenant_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Presence]:
        return Presence.objects.filter(tenant_id=tenant_id, user_id=user_id).first()
