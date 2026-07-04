"""Django application configuration for core infrastructure."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core infrastructure app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.core"
    verbose_name = "Core"
