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
    name = "backend.shared"
    verbose_name = "Shared"

    def ready(self) -> None:
        """Validate all shared sub-packages are importable."""
        import backend.shared.cache  # noqa: F401
        import backend.shared.constants  # noqa: F401
        import backend.shared.enums  # noqa: F401
        import backend.shared.event_bus  # noqa: F401
        import backend.shared.events  # noqa: F401
        import backend.shared.exceptions  # noqa: F401
        import backend.shared.pagination  # noqa: F401
        import backend.shared.permissions  # noqa: F401
        import backend.shared.search  # noqa: F401
        import backend.shared.security  # noqa: F401
        import backend.shared.storage  # noqa: F401
        import backend.shared.types  # noqa: F401
        import backend.shared.utils  # noqa: F401
        import backend.shared.validators  # noqa: F401
