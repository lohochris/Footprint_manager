# backend/intelligence/providers/__init__.py
"""Public surface of the intelligence.providers package.

Exports the provider contract, request/response models, registry helpers,
and the metadata/health models introduced in Sprint 3B.7.
"""

from .base import AIProvider
from .dummy_provider import DummyProvider
from .echo_provider import EchoProvider
from .mock_provider import MockProvider, MockScenario
from .provider_metadata import HealthStatus, ProviderCapabilities, ProviderMetadata
from .registry import ProviderRegistry, register_provider
from .request import AIRequest
from .response import AIResponse

__all__ = [
    # Core contract
    "AIProvider",
    # I/O models
    "AIRequest",
    "AIResponse",
    # Registry
    "ProviderRegistry",
    "register_provider",
    # Metadata models (Sprint 3B.7 Step 1)
    "ProviderCapabilities",
    "ProviderMetadata",
    "HealthStatus",
    # Test providers (Sprint 3B.7 Step 3)
    "MockProvider",
    "MockScenario",
    # Debug provider (Sprint 3B.7 Step 4)
    "EchoProvider",
    # Reference implementation
    "DummyProvider",
]
