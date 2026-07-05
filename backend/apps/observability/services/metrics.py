import uuid
from typing import Dict, Any, Optional, List
from .dto import MetricDTO
from ..engine.core import ObservabilityEngine
from ..selectors import MetricSelector

class MetricsService:
    @staticmethod
    def capture_metric(tenant_id: uuid.UUID, name: str, value: float, source: str = "", labels: Optional[Dict[str, Any]] = None) -> None:
        ObservabilityEngine.record_metric(tenant_id, name, value, source, labels)

    @staticmethod
    def get_recent_metrics(tenant_id: uuid.UUID, name: str, minutes: int = 60) -> List[MetricDTO]:
        metrics = MetricSelector.get_recent_metrics(tenant_id, name, minutes)
        return [
            MetricDTO(
                id=m.id,
                name=m.name,
                value=m.value,
                timestamp=m.timestamp,
                source=m.source,
                labels=m.labels
            ) for m in metrics
        ]
