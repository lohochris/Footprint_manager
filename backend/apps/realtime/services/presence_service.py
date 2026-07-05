import uuid
from typing import Optional
from ..repositories import PresenceRepository
from ..selectors import PresenceSelector
from .dto import PresenceDTO

class PresenceService:
    @staticmethod
    def update_status(tenant_id: uuid.UUID, user_id: uuid.UUID, status: str, active_workspace_id: Optional[uuid.UUID] = None) -> PresenceDTO:
        presence = PresenceRepository.update_presence(tenant_id, user_id, status, active_workspace_id)
        return PresenceDTO(
            user_id=presence.user_id,
            status=presence.status,
            last_heartbeat_at=presence.last_heartbeat_at
        )

    @staticmethod
    def get_presence(tenant_id: uuid.UUID, user_id: uuid.UUID) -> Optional[PresenceDTO]:
        presence = PresenceSelector.get_presence(tenant_id, user_id)
        if not presence:
            return None
        return PresenceDTO(
            user_id=presence.user_id,
            status=presence.status,
            last_heartbeat_at=presence.last_heartbeat_at
        )
