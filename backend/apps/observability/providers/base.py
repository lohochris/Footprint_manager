import uuid
from typing import Dict, Any, List, Optional
import datetime

class BaseMetricsProvider:
    def record_metric(self, tenant_id: uuid.UUID, name: str, value: float, source: str = "", labels: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError

class BaseTracingProvider:
    def record_trace(self, tenant_id: uuid.UUID, trace_id: str, span_id: str, name: str, start_time: datetime.datetime, end_time: Optional[datetime.datetime] = None, parent_span_id: Optional[str] = None, correlation_id: Optional[str] = None, causation_id: Optional[str] = None, status: str = "", tags: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError

class BaseLoggingProvider:
    def log(self, tenant_id: uuid.UUID, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError

class BaseAlertProvider:
    def dispatch_alert(self, tenant_id: uuid.UUID, alert_id: uuid.UUID, severity: str, source: str, message: str, details: Optional[Dict[str, Any]] = None, targets: Optional[List[str]] = None) -> None:
        raise NotImplementedError
