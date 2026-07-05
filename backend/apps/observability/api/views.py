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
        metrics = MetricsService.get_recent_metrics(request.user.tenant_id, name)
        return Response(MetricSerializer(metrics, many=True).data)

class HealthViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        health = HealthService.get_all_health(request.user.tenant_id)
        return Response(HealthSerializer(health, many=True).data)

class AlertViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        alerts = AlertService.get_active_alerts(request.user.tenant_id)
        return Response(AlertSerializer(alerts, many=True).data)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        AlertService.acknowledge_alert(request.user.tenant_id, pk)
        return Response({"status": "acknowledged"})

class TraceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        trace_id = request.query_params.get("trace_id")
        if not trace_id:
            return Response({"error": "Query parameter 'trace_id' is required"}, status=status.HTTP_400_BAD_REQUEST)
        tree = TraceService.get_trace_tree(request.user.tenant_id, trace_id)
        # Note: tree is a dict with "tree" -> list of DTOs.
        return Response({"tree": TraceSerializer(tree["tree"], many=True).data})

class DiagnosticViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    @action(detail=False, methods=['post'])
    def capture(self, request):
        snapshot = DiagnosticsService.capture_snapshot(request.user.tenant_id)
        return Response(snapshot)

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsObservabilityAdmin]

    def list(self, request):
        dashboard = DashboardService.get_dashboard(request.user.tenant_id)
        return Response(DashboardSerializer(dashboard).data)
