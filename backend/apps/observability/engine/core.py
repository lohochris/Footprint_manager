import uuid
import datetime
from typing import Dict, Any, Optional

from .aggregation import AggregationEngine
from .correlation import CorrelationEngine
from .evaluation import EvaluationEngine
from .diagnostics import DiagnosticsEngine
from ..providers.registry import ProviderRegistry

class ObservabilityEngine:
    """
    Coordinates operational monitoring across metrics, tracing, evaluation, and diagnostics.
    """

    @staticmethod
    def record_metric(tenant_id: uuid.UUID, name: str, value: float, source: str = "", labels: Optional[Dict[str, Any]] = None) -> None:
        # Write metric
        provider = ProviderRegistry.get_metrics_provider()
        provider.record_metric(tenant_id, name, value, source, labels)

        # Evaluate for alerts
        EvaluationEngine.evaluate_metric(tenant_id, name, value)

    @staticmethod
    def get_dashboard(tenant_id: uuid.UUID) -> Dict[str, Any]:
        from ..selectors import DashboardSelector
        return DashboardSelector.get_dashboard_summary(tenant_id)

    @staticmethod
    def capture_trace(tenant_id: uuid.UUID, trace_id: str, span_id: str, name: str, start_time: datetime.datetime, end_time: Optional[datetime.datetime] = None, parent_span_id: Optional[str] = None, correlation_id: Optional[str] = None, causation_id: Optional[str] = None, status: str = "", tags: Optional[Dict[str, Any]] = None) -> None:
        # For sprint 15 we are writing straight to the DB via Repository for traces as we haven't implemented a TracingProvider yet.
        from ..repositories import TraceRepository
        TraceRepository.capture_trace(tenant_id, trace_id, span_id, name, start_time, end_time, parent_span_id, correlation_id, causation_id, status, tags)

    @staticmethod
    def capture_diagnostics(tenant_id: uuid.UUID) -> Dict[str, Any]:
        return DiagnosticsEngine.capture_snapshot(tenant_id)
