from typing import Dict, Type
from .base import BaseWorkflowProvider
from .in_process import InProcessWorkflowProvider

class ProviderFactory:
    """
    Factory for instantiating the correct workflow provider.
    """
    _providers: Dict[str, Type[BaseWorkflowProvider]] = {
        "in_process": InProcessWorkflowProvider,
    }

    @classmethod
    def get_provider(cls, name: str = "in_process") -> BaseWorkflowProvider:
        provider_cls = cls._providers.get(name)
        if not provider_cls:
            raise ValueError(f"Unknown workflow provider: {name}")
        return provider_cls()
