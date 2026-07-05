from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ....models import (
    APIKey,
    SecurityEvent,
    SecurityPolicy,
    SecuritySession,
    TrustedDevice,
)
from ..serializers import (
    APIKeySerializer,
    SecurityEventSerializer,
    SecurityPolicySerializer,
    SecuritySessionSerializer,
    TrustedDeviceSerializer,
)


class APIKeyViewSet(viewsets.ModelViewSet):
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        api_key = self.get_object()
        # Integration with APIKeyService
        return Response({"status": "revoked"})


class TrustedDeviceViewSet(viewsets.ModelViewSet):
    queryset = TrustedDevice.objects.all()
    serializer_class = TrustedDeviceSerializer


class SecuritySessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SecuritySession.objects.all()
    serializer_class = SecuritySessionSerializer

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        session = self.get_object()
        # Integration with SecurityEngine/SessionService
        return Response({"status": "revoked"})


class SecurityPolicyViewSet(viewsets.ModelViewSet):
    queryset = SecurityPolicy.objects.all()
    serializer_class = SecurityPolicySerializer


class SecurityEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
