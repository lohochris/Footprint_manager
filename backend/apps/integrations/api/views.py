import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import IntegrationSerializer, SubscriptionSerializer, IntegrationEventSerializer
from .permissions import IntegrationManagePermission, WebhookReceiverPermission
from ..models import Integration, Subscription, IntegrationEvent
from ..services.integration_service import IntegrationService
from ..services.routing_service import EventRoutingService

class IntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationSerializer
    permission_classes = [IntegrationManagePermission]

    def get_queryset(self):
        return Integration.objects.filter(tenant_id=self.request.user.tenant_id)

    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IntegrationManagePermission]

    def get_queryset(self):
        return Subscription.objects.filter(tenant_id=self.request.user.tenant_id)

    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)

class IntegrationEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IntegrationEventSerializer
    permission_classes = [IntegrationManagePermission]

    def get_queryset(self):
        return IntegrationEvent.objects.filter(tenant_id=self.request.user.tenant_id)

class WebhookReceiverView(APIView):
    permission_classes = [WebhookReceiverPermission]

    def post(self, request, provider_id, *args, **kwargs):
        # Note: In a production scenario, provider_id would help map to the right integration and tenant
        # We need tenant_id from URL or Headers. For demonstration, we assume it's passed or derived.
        tenant_id_str = request.headers.get("X-Tenant-ID")
        integration_id_str = request.headers.get("X-Integration-ID")
        idempotency_key = request.headers.get("X-Idempotency-Key", str(uuid.uuid4()))

        if not tenant_id_str or not integration_id_str:
            return Response({"detail": "Missing tenant or integration headers"}, status=status.HTTP_400_BAD_REQUEST)

        tenant_id = uuid.UUID(tenant_id_str)
        integration_id = uuid.UUID(integration_id_str)

        EventRoutingService.handle_inbound_webhook(
            tenant_id=tenant_id,
            integration_id=integration_id,
            payload=request.data,
            idempotency_key=idempotency_key
        )
        return Response({"status": "received"}, status=status.HTTP_202_ACCEPTED)

class HealthView(APIView):
    permission_classes = [IntegrationManagePermission]

    def get(self, request):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
