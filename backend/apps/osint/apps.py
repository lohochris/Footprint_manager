# backend/apps/osint/apps.py
"""Django AppConfig for the OSINT Discovery bounded context."""

from django.apps import AppConfig


class OsintConfig(AppConfig):
    """AppConfig for the OSINT Discovery domain.

    The ``ready()`` hook imports the pipeline registry so that all
    ``PipelineFactory`` and ``PipelineRegistry`` entries are registered
    exactly once at application startup.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.osint"
    label = "osint"
    verbose_name = "OSINT Discovery"

    def ready(self) -> None:
        # Import registry to trigger PipelineFactory.register_stages()
        # and PipelineRegistry.register() calls.
        import backend.apps.osint.registry  # noqa: F401
