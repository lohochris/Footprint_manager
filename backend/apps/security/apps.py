from django.apps import AppConfig


class SecurityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.security"
    verbose_name = "Security"

    def ready(self) -> None:
        pass
