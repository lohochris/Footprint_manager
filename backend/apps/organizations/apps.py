"""Footprint Manager Organizations application."""

from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    def ready(self):
        # Import the registration side-effect to ensure operations are registered
        from . import registry
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.organizations"
    verbose_name = "Organizations"
