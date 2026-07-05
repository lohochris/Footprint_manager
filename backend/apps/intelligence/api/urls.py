from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EntityScoreViewSet,
    IntelligenceRecommendationViewSet,
    WatchlistEntryViewSet,
    InvestigationPriorityViewSet,
    IntelligenceOperationsViewSet,
)

app_name = "intelligence"

router = DefaultRouter()
router.register(r"scores", EntityScoreViewSet, basename="entityscore")
router.register(r"recommendations", IntelligenceRecommendationViewSet, basename="recommendation")
router.register(r"watchlists", WatchlistEntryViewSet, basename="watchlist")
router.register(r"priorities", InvestigationPriorityViewSet, basename="investigationpriority")
router.register(r"operations", IntelligenceOperationsViewSet, basename="operations")

urlpatterns = [
    path("", include(router.urls)),
]
