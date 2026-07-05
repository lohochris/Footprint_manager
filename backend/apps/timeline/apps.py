from django.apps import AppConfig


class TimelineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.timeline"
    verbose_name = "Timeline"

    def ready(self) -> None:
        try:
            import backend.apps.timeline.events.consumers  # noqa: F401
        except ImportError:
            pass
