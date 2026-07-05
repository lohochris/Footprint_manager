from typing import Dict, Optional
from .base import BaseNotificationProvider
from .in_app import InAppNotificationProvider

class ProviderRegistry:
    """Registry for pluggable notification providers."""

    def __init__(self):
        self._providers: Dict[str, BaseNotificationProvider] = {}
        self.register(InAppNotificationProvider())

    def register(self, provider: BaseNotificationProvider):
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> Optional[BaseNotificationProvider]:
        return self._providers.get(provider_id)

    def get_all(self) -> Dict[str, BaseNotificationProvider]:
        return self._providers

# Global registry instance
notification_provider_registry = ProviderRegistry()
