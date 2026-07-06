import contextlib

from django.apps import AppConfig


class ReportingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.reporting"
    verbose_name = "Reporting"

    def ready(self) -> None:
        with contextlib.suppress(ImportError):
            import backend.apps.reporting.events.consumers  # noqa: F401
