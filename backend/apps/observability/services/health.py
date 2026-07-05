import uuid
from typing import List, Optional
from .dto import HealthDTO
from ..repositories import HealthRepository
from ..selectors import HealthSelector

class HealthService:
    @staticmethod
    def update_health(tenant_id: uuid.UUID, component: str, status: str, response_time_ms: Optional[int] = None, failure_reason: str = "") -> None:
        HealthRepository.update_health(tenant_id, component, status, response_time_ms, failure_reason)

    @staticmethod
    def get_all_health(tenant_id: uuid.UUID) -> List[HealthDTO]:
        health_checks = HealthSelector.get_all_health(tenant_id)
        return [
            HealthDTO(
                id=h.id,
                component=h.component,
                status=h.status,
                response_time_ms=h.response_time_ms,
                last_check=h.last_check,
                failure_reason=h.failure_reason
            ) for h in health_checks
        ]
