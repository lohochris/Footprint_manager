"""Shared application for Footprint Manager cross-cutting utilities."""

from django.apps import AppConfig


class SharedConfig(AppConfig):
    """
    Django AppConfig for the shared package.

    The ``ready()`` hook performs a lightweight import smoke-test of all
    shared sub-packages to detect misconfiguration at startup rather than
    at the point of first use.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "shared"
    verbose_name = "Shared"

    def ready(self) -> None:
        """Validate all shared sub-packages are importable."""
        import shared.cache  # noqa: F401
        import shared.constants  # noqa: F401
        import shared.enums  # noqa: F401
        import shared.event_bus  # noqa: F401
        import shared.events  # noqa: F401
        import shared.exceptions  # noqa: F401
        import shared.pagination  # noqa: F401
        import shared.permissions  # noqa: F401
        import shared.search  # noqa: F401
        import shared.security  # noqa: F401
        import shared.storage  # noqa: F401
        import shared.types  # noqa: F401
        import shared.utils  # noqa: F401
        import shared.validators  # noqa: F401
