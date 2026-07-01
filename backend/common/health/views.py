"""Compatibility exports for health views."""

from core.health.views import HealthCheckView, ReadinessCheckView

__all__ = ["HealthCheckView", "ReadinessCheckView"]
