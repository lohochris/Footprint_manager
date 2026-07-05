from typing import Any, Dict
from .base import BaseRealtimeProvider

class ServerSentEventsProvider(BaseRealtimeProvider):
    @property
    def protocol_name(self) -> str:
        return "sse"

    def broadcast(self, channel_id: str, event_type: str, payload: Dict[str, Any]) -> bool:
        # Stub: Future SSE implementation
        return True

    def send_to_connection(self, connection_id: str, event_type: str, payload: Dict[str, Any]) -> bool:
        # Stub
        return True

    def disconnect(self, connection_id: str) -> bool:
        # Stub
        return True
