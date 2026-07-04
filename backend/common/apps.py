"""Common application for Footprint Manager shared infrastructure."""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.common"
    verbose_name = "Common"
