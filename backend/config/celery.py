"""Celery application instance for Footprint Manager."""

import os

from celery import Celery
from celery.signals import setup_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings.development")

app = Celery("footprint_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@setup_logging.connect
def configure_celery_logging(**_kwargs: object) -> None:
    """Use Django's structlog configuration for Celery workers."""
    from django.conf import settings

    if hasattr(settings, "LOGGING"):
        import logging.config

        logging.config.dictConfig(settings.LOGGING)


@app.task(bind=True, ignore_result=True)
def debug_task(self: object) -> None:
    """Diagnostic task for verifying Celery connectivity."""
    import structlog

    logger = structlog.get_logger(__name__)
    logger.info("celery_debug_task", request=str(self))
