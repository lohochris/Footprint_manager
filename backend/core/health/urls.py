"""Health check URL routes."""

from core.health.views import HealthCheckView, ReadinessCheckView
from django.urls import path

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health-check"),
    path("ready/", ReadinessCheckView.as_view(), name="readiness-check"),
    path("live/", HealthCheckView.as_view(), name="liveness-check"),
]
