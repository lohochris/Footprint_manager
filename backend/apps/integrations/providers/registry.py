from typing import Dict, Optional
from .base import BaseIntegrationProvider
from .rest import RESTProvider
from .webhook import WebhookProvider
from .secrets import LocalEncryptedSecretsProvider

class IntegrationProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseIntegrationProvider] = {}
        self.register(RESTProvider())
        self.register(WebhookProvider())

    def register(self, provider: BaseIntegrationProvider):
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> Optional[BaseIntegrationProvider]:
        return self._providers.get(provider_id)

integration_provider_registry = IntegrationProviderRegistry()
secrets_provider = LocalEncryptedSecretsProvider()
