import uuid
from .dto import DashboardDTO
from ..engine.core import ObservabilityEngine

class DashboardService:
    @staticmethod
    def get_dashboard(tenant_id: uuid.UUID) -> DashboardDTO:
        data = ObservabilityEngine.get_dashboard(tenant_id)
        return DashboardDTO(
            active_alerts=data.get("active_alerts", 0),
            failed_integrations_24h=data.get("failed_integrations_24h", 0.0),
            ai_tokens_24h=data.get("ai_tokens_24h", 0.0)
        )
