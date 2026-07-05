from typing import Dict, Type
from .base import BaseRealtimeProvider
from .websocket import WebSocketProvider
from .sse import ServerSentEventsProvider

class ProviderRegistry:
    _providers: Dict[str, BaseRealtimeProvider] = {}

    @classmethod
    def register(cls, provider: BaseRealtimeProvider):
        cls._providers[provider.protocol_name] = provider

    @classmethod
    def get_provider(cls, protocol_name: str) -> BaseRealtimeProvider:
        if protocol_name not in cls._providers:
            raise ValueError(f"Provider for protocol '{protocol_name}' not found.")
        return cls._providers[protocol_name]

# Default registrations
ProviderRegistry.register(WebSocketProvider())
ProviderRegistry.register(ServerSentEventsProvider())
