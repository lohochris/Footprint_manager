# backend/intelligence/providers/base.py
"""Abstract AI Provider interface.

Providers will implement concrete AI vendor integrations in later sprints.
This file defines the contract only – no network calls or vendor logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AIProvider(ABC):
    """Base class for all AI providers.

    Each method should be overridden by concrete implementations. The default
    implementations raise ``NotImplementedError`` to signal that the provider
    does not support the operation.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Perform any required initialization (e.g., load credentials).

        Must be safe to call multiple times. Implementations should raise
        ``RuntimeError`` if initialization fails.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return a health dictionary describing provider status.

        Typical keys: ``available``, ``configured``, ``enabled``, ``version``.
        """
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return a list of capability names offered by the provider.

        Capability names correspond to the identifiers defined in
        ``backend.intelligence.providers.capability``.
        """
        raise NotImplementedError

    @abstractmethod
    def supports(self, task: str) -> bool:
        """Return ``True`` if the provider can handle the given ``task``.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, request: "AIRequest") -> "AIResponse":
        """Execute an AI request and return a response.

        Concrete providers will perform the actual inference. For now the
        method is abstract and must be overridden.
        """
        raise NotImplementedError
