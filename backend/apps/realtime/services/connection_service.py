import uuid
from typing import Dict, Any, Optional
from ..repositories import ConnectionRepository
from ..selectors import ConnectionSelector
from .dto import ConnectionDTO

class ConnectionService:
    @staticmethod
    def register_connection(tenant_id: uuid.UUID, user_id: uuid.UUID, protocol: str, session_id: str, client_metadata: Optional[Dict[str, Any]] = None) -> ConnectionDTO:
        conn = ConnectionRepository.create(tenant_id, user_id, protocol, session_id, client_metadata)
        return ConnectionDTO(
            id=conn.id,
            tenant_id=conn.tenant_id,
            user_id=conn.user_id,
            protocol=conn.protocol,
            session_id=conn.session_id,
            state=conn.state
        )

    @staticmethod
    def heartbeat(tenant_id: uuid.UUID, session_id: str) -> None:
        conn = ConnectionSelector.get_connection(tenant_id, session_id)
        if conn:
            ConnectionRepository.update_heartbeat(conn.id)

    @staticmethod
    def disconnect(tenant_id: uuid.UUID, session_id: str) -> None:
        conn = ConnectionSelector.get_connection(tenant_id, session_id)
        if conn:
            ConnectionRepository.disconnect(conn.id)
