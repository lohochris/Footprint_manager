import uuid
from typing import Dict, Any, List, Optional
from django.utils import timezone
import datetime
from .models import Metric, HealthCheck, AlertRule, Alert, Trace, DiagnosticSnapshot

class MetricRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, name: str, value: float, source: str = "", labels: Optional[Dict[str, Any]] = None) -> Metric:
        return Metric.objects.create(
            tenant_id=tenant_id,
            name=name,
            value=value,
            source=source,
            labels=labels or {},
            timestamp=timezone.now()
        )

class HealthRepository:
    @staticmethod
    def update_health(tenant_id: uuid.UUID, component: str, status: str, response_time_ms: Optional[int] = None, failure_reason: str = "") -> HealthCheck:
        hc, _ = HealthCheck.objects.update_or_create(
            tenant_id=tenant_id,
            component=component,
            defaults={
                "status": status,
                "response_time_ms": response_time_ms,
                "failure_reason": failure_reason,
            }
        )
        return hc

class AlertRepository:
    @staticmethod
    def create_alert(tenant_id: uuid.UUID, severity: str, source: str, details: Optional[Dict[str, Any]] = None, rule_id: Optional[uuid.UUID] = None) -> Alert:
        return Alert.objects.create(
            tenant_id=tenant_id,
            severity=severity,
            source=source,
            details=details or {},
            rule_id=rule_id
        )

    @staticmethod
    def acknowledge(tenant_id: uuid.UUID, alert_id: uuid.UUID) -> None:
        Alert.objects.filter(tenant_id=tenant_id, id=alert_id).update(acknowledged_at=timezone.now())

    @staticmethod
    def resolve(tenant_id: uuid.UUID, alert_id: uuid.UUID) -> None:
        Alert.objects.filter(tenant_id=tenant_id, id=alert_id).update(resolved_at=timezone.now())

class TraceRepository:
    @staticmethod
    def capture_trace(tenant_id: uuid.UUID, trace_id: str, span_id: str, name: str, start_time: datetime.datetime, end_time: Optional[datetime.datetime] = None, parent_span_id: Optional[str] = None, correlation_id: Optional[str] = None, causation_id: Optional[str] = None, status: str = "", tags: Optional[Dict[str, Any]] = None) -> Trace:
        duration_ms = None
        if end_time:
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

        return Trace.objects.create(
            tenant_id=tenant_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            name=name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            status=status,
            tags=tags or {}
        )

class DiagnosticRepository:
    @staticmethod
    def capture_snapshot(tenant_id: uuid.UUID, component_health: Dict[str, Any], active_connections: int, queue_statistics: Dict[str, Any], provider_status: Dict[str, Any], recent_failures: List[Dict[str, Any]]) -> DiagnosticSnapshot:
        return DiagnosticSnapshot.objects.create(
            tenant_id=tenant_id,
            component_health=component_health,
            active_connections=active_connections,
            queue_statistics=queue_statistics,
            provider_status=provider_status,
            recent_failures=recent_failures
        )
