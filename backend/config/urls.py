"""URL configuration for Footprint Manager."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", include("backend.core.health.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/", include("backend.apps.investigations.api.router")),
    path("api/v1/", include("backend.apps.evidence.api.router")),
    path("api/v1/identity/", include("backend.apps.identity.api.urls")),
    path("api/v1/graph/", include("backend.apps.graph.api.urls")),
    path("api/v1/intelligence/", include("backend.apps.intelligence.api.urls")),
    path("api/v1/ai/", include("backend.apps.ai_assistant.api.urls")),
    path("api/v1/orchestration/", include("backend.apps.orchestration.api.urls")),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
