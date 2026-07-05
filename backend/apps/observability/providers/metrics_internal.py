import uuid
from typing import Dict, Any, Optional
from .base import BaseMetricsProvider
from ..repositories import MetricRepository

class InternalMetricsProvider(BaseMetricsProvider):
    """
    Default provider that stores metrics directly in the Footprint Manager database.
    """
    def record_metric(self, tenant_id: uuid.UUID, name: str, value: float, source: str = "", labels: Optional[Dict[str, Any]] = None) -> None:
        MetricRepository.create(
            tenant_id=tenant_id,
            name=name,
            value=value,
            source=source,
            labels=labels
        )
