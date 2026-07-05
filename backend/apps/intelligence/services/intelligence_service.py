from typing import Any
from django.core.exceptions import ValidationError
from backend.apps.common.pipeline.core import BaseService, ExecutionResult

# Ensure registry is loaded to map pipeline operations
import backend.apps.intelligence.pipelines.registry

class IntelligenceService:
    """Domain service interface for the Intelligence Analytics context."""

    @staticmethod
    def calculate(
        user: Any,
        tenant: Any,
        workspace_id: Any = None,
    ) -> dict[str, Any]:
        """Triggers the intelligence.calculate pipeline."""
        payload = {"workspace_id": str(workspace_id) if workspace_id else None}
        result: ExecutionResult = BaseService.execute(
            operation="intelligence.calculate",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )
        if not result.success:
            raise result.error or ValidationError("Intelligence calculate pipeline failed.")
        return result.data or {}

    @staticmethod
    def refresh(
        user: Any,
        tenant: Any,
        workspace_id: Any = None,
    ) -> dict[str, Any]:
        """Triggers the intelligence.refresh pipeline."""
        payload = {"workspace_id": str(workspace_id) if workspace_id else None}
        result: ExecutionResult = BaseService.execute(
            operation="intelligence.refresh",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )
        if not result.success:
            raise result.error or ValidationError("Intelligence refresh pipeline failed.")
        return result.data or {}
