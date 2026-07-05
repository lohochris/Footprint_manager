from dataclasses import dataclass, field
import uuid
from typing import Dict, Any, List, Optional
import datetime

@dataclass(frozen=True)
class MetricDTO:
    id: uuid.UUID
    name: str
    value: float
    timestamp: datetime.datetime
    source: str
    labels: Dict[str, Any]

@dataclass(frozen=True)
class HealthDTO:
    id: uuid.UUID
    component: str
    status: str
    response_time_ms: Optional[int]
    last_check: datetime.datetime
    failure_reason: str

@dataclass(frozen=True)
class AlertRuleDTO:
    id: uuid.UUID
    name: str
    metric_name: str
    threshold: float
    condition: str
    severity: str
    is_active: bool

@dataclass(frozen=True)
class AlertDTO:
    id: uuid.UUID
    severity: str
    source: str
    trigger_time: datetime.datetime
    resolved_at: Optional[datetime.datetime]
    details: Dict[str, Any]

@dataclass(frozen=True)
class TraceDTO:
    id: uuid.UUID
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    duration_ms: Optional[int]
    status: str

@dataclass(frozen=True)
class DiagnosticDTO:
    id: uuid.UUID
    captured_at: datetime.datetime
    component_health: Dict[str, Any]
    active_connections: int

@dataclass(frozen=True)
class DashboardDTO:
    active_alerts: int
    failed_integrations_24h: float
    ai_tokens_24h: float
