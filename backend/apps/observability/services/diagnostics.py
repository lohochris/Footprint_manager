import uuid
from typing import Dict, Any
from .dto import DiagnosticDTO
from ..engine.core import ObservabilityEngine

class DiagnosticsService:
    @staticmethod
    def capture_snapshot(tenant_id: uuid.UUID) -> Dict[str, Any]:
        return ObservabilityEngine.capture_diagnostics(tenant_id)
