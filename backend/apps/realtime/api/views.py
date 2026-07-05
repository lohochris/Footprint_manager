from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import (
    ChannelSerializer,
    ConnectionSerializer,
    SubscriptionSerializer,
    PresenceSerializer,
    StreamAuditSerializer
)
from .permissions import IsRealtimeUser
from ..models import RealtimeChannel, Connection, Subscription, Presence, StreamAudit
from ..services.presence_service import PresenceService
from ..services.connection_service import ConnectionService

class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChannelSerializer
    permission_classes = [IsRealtimeUser]

    def get_queryset(self):
        return RealtimeChannel.objects.filter(tenant_id=self.request.user.tenant_id)

class ConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [IsRealtimeUser]

    def get_queryset(self):
        return Connection.objects.filter(tenant_id=self.request.user.tenant_id, user=self.request.user)

    @extend_schema(responses={200: dict})
    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        connection = self.get_object()
        ConnectionService.heartbeat(request.user.tenant_id, connection.session_id)
        return Response({"status": "heartbeat recorded"})

class SubscriptionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsRealtimeUser]

    def get_queryset(self):
        return Subscription.objects.filter(tenant_id=self.request.user.tenant_id, user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id, user=self.request.user)

class PresenceViewSet(viewsets.ModelViewSet):
    serializer_class = PresenceSerializer
    permission_classes = [IsRealtimeUser]

    def get_queryset(self):
        return Presence.objects.filter(tenant_id=self.request.user.tenant_id)

    def perform_create(self, serializer):
        # We enforce user context
        serializer.save(tenant_id=self.request.user.tenant_id, user=self.request.user)

class StreamAuditViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StreamAuditSerializer
    permission_classes = [IsRealtimeUser]

    def get_queryset(self):
        return StreamAudit.objects.filter(tenant_id=self.request.user.tenant_id)
