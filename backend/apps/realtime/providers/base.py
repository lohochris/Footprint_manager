import abc
from typing import Any, Dict

class BaseRealtimeProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def protocol_name(self) -> str:
        """E.g., 'websocket', 'sse'"""
        pass

    @abc.abstractmethod
    def broadcast(self, channel_id: str, event_type: str, payload: Dict[str, Any]) -> bool:
        """Broadcasts an event to all subscribers of a channel."""
        pass

    @abc.abstractmethod
    def send_to_connection(self, connection_id: str, event_type: str, payload: Dict[str, Any]) -> bool:
        """Sends an event directly to a specific connection."""
        pass

    @abc.abstractmethod
    def disconnect(self, connection_id: str) -> bool:
        """Forcefully disconnects a client."""
        pass
