from django.apps import AppConfig


class InvestigationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.investigations"
    label = "investigations"

    def ready(self):
        from . import registry
