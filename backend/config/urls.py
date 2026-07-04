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
