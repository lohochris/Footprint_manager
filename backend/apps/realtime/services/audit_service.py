import uuid
from typing import Dict, Any, Optional
from ..repositories import StreamAuditRepository

class AuditService:
    @staticmethod
    def log_action(tenant_id: uuid.UUID, connection_id: uuid.UUID, action: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        StreamAuditRepository.create(
            tenant_id=tenant_id,
            connection_id=connection_id,
            action=action,
            status=status,
            details=details or {}
        )
