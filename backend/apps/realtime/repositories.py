import uuid
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import RealtimeChannel, Connection, Subscription, StreamEvent, Presence, StreamAudit

User = get_user_model()

class ChannelRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, channel_type: str, resource_identifier: str, permissions_required: Optional[List[str]] = None) -> RealtimeChannel:
        return RealtimeChannel.objects.create(
            tenant_id=tenant_id,
            channel_type=channel_type,
            resource_identifier=resource_identifier,
            permissions_required=permissions_required or []
        )

class ConnectionRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, user_id: uuid.UUID, protocol: str, session_id: str, client_metadata: Optional[Dict[str, Any]] = None) -> Connection:
        return Connection.objects.create(
            tenant_id=tenant_id,
            user_id=user_id,
            protocol=protocol,
            session_id=session_id,
            client_metadata=client_metadata or {},
            state=Connection.State.CONNECTED,
            last_heartbeat_at=timezone.now()
        )

    @staticmethod
    def update_heartbeat(connection_id: uuid.UUID) -> None:
        Connection.objects.filter(id=connection_id).update(last_heartbeat_at=timezone.now())

    @staticmethod
    def disconnect(connection_id: uuid.UUID) -> None:
        Connection.objects.filter(id=connection_id).update(state=Connection.State.DISCONNECTED)

class SubscriptionRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, user_id: uuid.UUID, channel_id: uuid.UUID, connection_id: uuid.UUID) -> Subscription:
        return Subscription.objects.create(
            tenant_id=tenant_id,
            user_id=user_id,
            channel_id=channel_id,
            connection_id=connection_id,
            status=Subscription.Status.ACTIVE
        )

    @staticmethod
    def deactivate(subscription_id: uuid.UUID) -> None:
        Subscription.objects.filter(id=subscription_id).update(status=Subscription.Status.INACTIVE)

class StreamEventRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, channel_id: uuid.UUID, event_type: str, payload: Dict[str, Any], correlation_id: Optional[str] = None, causation_id: Optional[str] = None, idempotency_key: Optional[str] = None) -> StreamEvent:
        return StreamEvent.objects.create(
            tenant_id=tenant_id,
            channel_id=channel_id,
            event_type=event_type,
            payload=payload,
            correlation_id=correlation_id,
            causation_id=causation_id,
            idempotency_key=idempotency_key
        )

    @staticmethod
    def mark_delivered(event_id: int) -> None:
        StreamEvent.objects.filter(sequence_number=event_id).update(status=StreamEvent.Status.DELIVERED)

class PresenceRepository:
    @staticmethod
    def update_presence(tenant_id: uuid.UUID, user_id: uuid.UUID, status: str, active_workspace_id: Optional[uuid.UUID] = None, connected_devices: Optional[int] = None) -> Presence:
        presence, created = Presence.objects.get_or_create(
            tenant_id=tenant_id,
            user_id=user_id,
            defaults={"status": status}
        )
        if not created:
            presence.status = status
            presence.last_heartbeat_at = timezone.now()
            if active_workspace_id is not None:
                presence.active_workspace_id = active_workspace_id
            if connected_devices is not None:
                presence.connected_devices = connected_devices
            presence.save()
        return presence

class StreamAuditRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, connection_id: uuid.UUID, action: str, status: str, details: Dict[str, Any]) -> StreamAudit:
        return StreamAudit.objects.create(
            tenant_id=tenant_id,
            connection_id=connection_id,
            action=action,
            status=status,
            details=details
        )
