from django.apps import AppConfig


class IdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.identity"
    verbose_name = "Identity Resolution"

    def ready(self):
        from . import registry  # noqa
