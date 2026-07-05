import uuid
from typing import List
from .dto import AlertDTO
from ..repositories import AlertRepository
from ..selectors import AlertSelector

class AlertService:
    @staticmethod
    def get_active_alerts(tenant_id: uuid.UUID) -> List[AlertDTO]:
        alerts = AlertSelector.get_active_alerts(tenant_id)
        return [
            AlertDTO(
                id=a.id,
                severity=a.severity,
                source=a.source,
                trigger_time=a.trigger_time,
                resolved_at=a.resolved_at,
                details=a.details
            ) for a in alerts
        ]

    @staticmethod
    def acknowledge_alert(tenant_id: uuid.UUID, alert_id: uuid.UUID) -> None:
        AlertRepository.acknowledge(tenant_id, alert_id)
