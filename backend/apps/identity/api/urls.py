from django.urls import include, path
from rest_framework.routers import DefaultRouter
from backend.apps.identity.api.views import (
    IdentityViewSet,
    IdentityAttributeViewSet,
    IdentityRelationshipViewSet,
    IdentityMatchViewSet,
    IdentityMergeHistoryViewSet,
)

router = DefaultRouter()
router.register(r"identities", IdentityViewSet, basename="identity")
router.register(r"attributes", IdentityAttributeViewSet, basename="identity-attribute")
router.register(r"relationships", IdentityRelationshipViewSet, basename="identity-relationship")
router.register(r"matches", IdentityMatchViewSet, basename="identity-match")
router.register(r"merge-history", IdentityMergeHistoryViewSet, basename="identity-merge-history")

urlpatterns = [
    path("", include(router.urls)),
]
