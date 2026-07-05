from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssistantSessionViewSet

router = DefaultRouter()
router.register(r"sessions", AssistantSessionViewSet, basename="assistant-session")

urlpatterns = [
    path("", include(router.urls)),
]
