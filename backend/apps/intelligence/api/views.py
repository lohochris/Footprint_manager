from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema

from backend.apps.intelligence.models import (
    EntityScore,
    IntelligenceRecommendation,
    WatchlistEntry,
    InvestigationPriority,
)
from backend.apps.intelligence.api.serializers import (
    EntityScoreSerializer,
    IntelligenceRecommendationSerializer,
    WatchlistEntrySerializer,
    InvestigationPrioritySerializer,
)
from backend.apps.intelligence.services.intelligence_service import IntelligenceService

class IntelligenceOperationsViewSet(viewsets.ViewSet):
    """Endpoints for orchestrating intelligence pipelines."""

    @extend_schema(responses={200: dict})
    @action(detail=False, methods=["post"])
    def calculate(self, request: Request) -> Response:
        """Trigger intelligence calculations for the tenant/workspace."""
        workspace_id = request.data.get("workspace_id")

        try:
            IntelligenceService.calculate(
                user=request.user,
                tenant=getattr(request.user, "tenant", None),
                workspace_id=workspace_id,
            )
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Intelligence calculated successfully"})

    @extend_schema(responses={200: dict})
    @action(detail=False, methods=["post"])
    def refresh(self, request: Request) -> Response:
        """Clear existing intelligence and compute fresh."""
        workspace_id = request.data.get("workspace_id")

        try:
            IntelligenceService.refresh(
                user=request.user,
                tenant=getattr(request.user, "tenant", None),
                workspace_id=workspace_id,
            )
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Intelligence refreshed successfully"})


class EntityScoreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EntityScoreSerializer

    def get_queryset(self):
        return EntityScore.objects.filter(tenant_id=self.request.user.tenant_id)


class IntelligenceRecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = IntelligenceRecommendationSerializer

    def get_queryset(self):
        return IntelligenceRecommendation.objects.filter(tenant_id=self.request.user.tenant_id)


class WatchlistEntryViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistEntrySerializer

    def get_queryset(self):
        return WatchlistEntry.objects.filter(tenant_id=self.request.user.tenant_id)


class InvestigationPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvestigationPrioritySerializer

    def get_queryset(self):
        return InvestigationPriority.objects.filter(tenant_id=self.request.user.tenant_id)
