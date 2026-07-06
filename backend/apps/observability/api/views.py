from backend.shared.utils.tenant_resolver import get_tenant_id_for_user
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsObservabilityAdmin
from .serializers import MetricSerializer, HealthSerializer, AlertSerializer, TraceSerializer, DiagnosticSerializer, DashboardSerializer
from ..services import MetricsService, HealthService, AlertService, TraceService, DashboardService, DiagnosticsService

class MetricsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        name = request.query_params.get("name")
        if not name:
            return Response({"error": "Query parameter 'name' is required"}, status=status.HTTP_400_BAD_REQUEST)
        metrics = MetricsService.get_recent_metrics(get_tenant_id_for_user(request.user), name)
        return Response(MetricSerializer(metrics, many=True).data)

class HealthViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        workspace_id = request.query_params.get("workspace")
        if not workspace_id:
            return Response({"error": "Query parameter 'workspace' is required"}, status=status.HTTP_400_BAD_REQUEST)

        from backend.shared.utils.tenant_resolver import resolve_workspace
        from django.core.exceptions import ValidationError, PermissionDenied

        try:
            workspace = resolve_workspace(request.user, workspace_id)
        except (ValidationError, PermissionDenied) as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        health = HealthService.get_all_health(workspace.id)

        # Aggregate into expected JSON schema for frontend
        components = {h.component: h.status for h in health}
        overall_status = "HEALTHY"
        if any(h.status == "UNHEALTHY" for h in health):
            overall_status = "UNHEALTHY"
        elif any(h.status == "DEGRADED" for h in health):
            overall_status = "DEGRADED"

        last_checked = max((h.last_check for h in health), default=None)

        return Response({
            "status": overall_status,
            "components": components,
            "last_checked": last_checked
        })

class AlertViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        alerts = AlertService.get_active_alerts(get_tenant_id_for_user(request.user))
        return Response(AlertSerializer(alerts, many=True).data)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        AlertService.acknowledge_alert(get_tenant_id_for_user(request.user), pk)
        return Response({"status": "acknowledged"})

class TraceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        trace_id = request.query_params.get("trace_id")
        if not trace_id:
            return Response({"error": "Query parameter 'trace_id' is required"}, status=status.HTTP_400_BAD_REQUEST)
        tree = TraceService.get_trace_tree(get_tenant_id_for_user(request.user), trace_id)
        # Note: tree is a dict with "tree" -> list of DTOs.
        return Response({"tree": TraceSerializer(tree["tree"], many=True).data})

class DiagnosticViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    @action(detail=False, methods=['post'])
    def capture(self, request):
        snapshot = DiagnosticsService.capture_snapshot(get_tenant_id_for_user(request.user))
        return Response(snapshot)

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        dashboard = DashboardService.get_dashboard(get_tenant_id_for_user(request.user))
        return Response(DashboardSerializer(dashboard).data)
