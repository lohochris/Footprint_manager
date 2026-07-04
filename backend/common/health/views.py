"""Compatibility exports for health views."""

from backend.core.health.views import HealthCheckView, ReadinessCheckView

__all__ = ["HealthCheckView", "ReadinessCheckView"]
