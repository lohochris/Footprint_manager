import uuid
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import Metric, HealthCheck, AlertRule, Alert, Trace, DiagnosticSnapshot

class MetricSelector:
    @staticmethod
    def get_recent_metrics(tenant_id: uuid.UUID, name: str, minutes: int = 60) -> QuerySet[Metric]:
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return Metric.objects.filter(tenant_id=tenant_id, name=name, timestamp__gte=cutoff)

class HealthSelector:
    @staticmethod
    def get_all_health(tenant_id: uuid.UUID) -> QuerySet[HealthCheck]:
        return HealthCheck.objects.filter(tenant_id=tenant_id)

class AlertSelector:
    @staticmethod
    def get_active_alerts(tenant_id: uuid.UUID) -> QuerySet[Alert]:
        return Alert.objects.filter(tenant_id=tenant_id, resolved_at__isnull=True)

class TraceSelector:
    @staticmethod
    def get_trace_tree(tenant_id: uuid.UUID, trace_id: str) -> QuerySet[Trace]:
        return Trace.objects.filter(tenant_id=tenant_id, trace_id=trace_id).order_by('start_time')

class DashboardSelector:
    @staticmethod
    def get_dashboard_summary(tenant_id: uuid.UUID) -> Dict[str, Any]:
        cutoff_24h = timezone.now() - timedelta(hours=24)

        # Aggregations for the dashboard
        active_alerts_count = Alert.objects.filter(tenant_id=tenant_id, resolved_at__isnull=True).count()
        failed_integrations = Metric.objects.filter(tenant_id=tenant_id, name="integrations_failed", timestamp__gte=cutoff_24h).aggregate(total=Sum('value'))['total'] or 0
        ai_tokens = Metric.objects.filter(tenant_id=tenant_id, name="ai_tokens_used", timestamp__gte=cutoff_24h).aggregate(total=Sum('value'))['total'] or 0

        return {
            "active_alerts": active_alerts_count,
            "failed_integrations_24h": failed_integrations,
            "ai_tokens_24h": ai_tokens
        }
