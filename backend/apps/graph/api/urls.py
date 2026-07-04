from django.urls import include, path
from rest_framework.routers import DefaultRouter

from backend.apps.graph.api.views import (
    GraphEdgeViewSet,
    GraphNodeViewSet,
    GraphSnapshotViewSet,
    GraphTraversalViewSet,
)

router = DefaultRouter()
router.register(r"nodes", GraphNodeViewSet, basename="node")
router.register(r"edges", GraphEdgeViewSet, basename="edge")
router.register(r"snapshots", GraphSnapshotViewSet, basename="snapshot")
router.register(r"traversal", GraphTraversalViewSet, basename="traversal")

urlpatterns = [
    path("", include(router.urls)),
]
