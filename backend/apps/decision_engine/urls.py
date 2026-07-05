from django.urls import include, path
from rest_framework.routers import DefaultRouter

from backend.apps.decision_engine.api.views import DecisionViewSet, PolicyViewSet

router = DefaultRouter()
router.register(r"policies", PolicyViewSet, basename="policy")
router.register(r"decisions", DecisionViewSet, basename="decision")

urlpatterns = [
    path("", include(router.urls)),
]
