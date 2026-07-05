import uuid
from typing import Dict, Any, List

class DiagnosticsEngine:
    @staticmethod
    def capture_snapshot(tenant_id: uuid.UUID) -> Dict[str, Any]:
        """
        Captures a diagnostic snapshot.
        """
        from ..selectors import HealthSelector

        health_checks = HealthSelector.get_all_health(tenant_id)
        component_health = {hc.component: hc.status for hc in health_checks}

        # Stubs for what would be real system queries
        active_connections = 0
        queue_statistics = {"tasks": 0}
        provider_status = {"database": "ok"}
        recent_failures: List[Dict[str, Any]] = []

        from ..repositories import DiagnosticRepository
        snapshot = DiagnosticRepository.capture_snapshot(
            tenant_id=tenant_id,
            component_health=component_health,
            active_connections=active_connections,
            queue_statistics=queue_statistics,
            provider_status=provider_status,
            recent_failures=recent_failures
        )

        return {
            "snapshot_id": str(snapshot.id),
            "captured_at": snapshot.captured_at
        }
