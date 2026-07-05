import uuid
from typing import Dict, Any

class AggregationEngine:
    @staticmethod
    def aggregate_metrics(tenant_id: uuid.UUID, metric_name: str, window_minutes: int) -> Dict[str, Any]:
        """
        Aggregates metrics for a given window.
        """
        # Note: Handled heavily by Selectors, this coordinates across metrics
        from ..selectors import MetricSelector
        metrics = MetricSelector.get_recent_metrics(tenant_id, metric_name, minutes=window_minutes)
        total = sum(m.value for m in metrics)
        count = metrics.count()
        avg = total / count if count > 0 else 0
        return {
            "metric": metric_name,
            "total": total,
            "average": avg,
            "count": count
        }
