from django.apps import AppConfig


class GovernanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.governance"
    verbose_name = "Governance"

    def ready(self) -> None:
        try:
            import backend.apps.governance.events.consumers  # noqa: F401
        except ImportError:
            pass
