from typing import Dict, Type
from .base import BaseMetricsProvider, BaseTracingProvider, BaseLoggingProvider, BaseAlertProvider
from .metrics_internal import InternalMetricsProvider
from .logging_structured import StructuredLoggingProvider

class ProviderRegistry:
    _metrics_providers: Dict[str, Type[BaseMetricsProvider]] = {
        "internal": InternalMetricsProvider
    }
    _logging_providers: Dict[str, Type[BaseLoggingProvider]] = {
        "structured": StructuredLoggingProvider
    }

    # Defaults
    _active_metrics = "internal"
    _active_logging = "structured"

    @classmethod
    def get_metrics_provider(cls) -> BaseMetricsProvider:
        provider_class = cls._metrics_providers.get(cls._active_metrics, InternalMetricsProvider)
        return provider_class()

    @classmethod
    def get_logging_provider(cls) -> BaseLoggingProvider:
        provider_class = cls._logging_providers.get(cls._active_logging, StructuredLoggingProvider)
        return provider_class()
