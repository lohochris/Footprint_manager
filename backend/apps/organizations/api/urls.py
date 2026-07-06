from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.organization_viewset import OrganizationViewSet
from .views.workspace_viewset import WorkspaceViewSet

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"workspaces", WorkspaceViewSet, basename="workspace")

urlpatterns = [
    path("", include(router.urls)),
]
