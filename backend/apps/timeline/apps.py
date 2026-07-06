import contextlib

from django.apps import AppConfig


class TimelineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.timeline"
    verbose_name = "Timeline"

    def ready(self) -> None:
        with contextlib.suppress(ImportError):
            import backend.apps.timeline.events.consumers  # noqa: F401
