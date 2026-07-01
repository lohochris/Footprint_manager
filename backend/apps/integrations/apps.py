"""
Integrations application for Footprint Manager.

This app provides clean interface abstractions and factory utilities for all
external service integrations.  No concrete provider implementations are
included here — those reside in environment-specific configuration or
dedicated provider packages.

Sub-modules
-----------
email           EmailBackend interface for transactional email.
openai          OpenAI LLM client interface.
claude          Anthropic Claude LLM client interface.
neo4j           Neo4j graph database client interface.
elasticsearch   Elasticsearch / OpenSearch client interface.
kafka           Apache Kafka message broker interface.
storage         File storage integration (wraps shared.storage).
"""

from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """Django AppConfig for the integrations package."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integrations"
    verbose_name = "Integrations"

    def ready(self) -> None:
        """Validate sub-module availability at startup."""
        import apps.integrations.claude  # noqa: F401
        import apps.integrations.elasticsearch  # noqa: F401
        import apps.integrations.email  # noqa: F401
        import apps.integrations.kafka  # noqa: F401
        import apps.integrations.neo4j  # noqa: F401
        import apps.integrations.openai  # noqa: F401
        import apps.integrations.storage  # noqa: F401
