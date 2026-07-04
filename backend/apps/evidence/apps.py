from django.apps import AppConfig


class EvidenceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.evidence"
    verbose_name = "Evidence Management"

    def ready(self):
        from . import registry

