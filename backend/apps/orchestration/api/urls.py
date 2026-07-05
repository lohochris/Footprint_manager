from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrchestrationViewSet

router = DefaultRouter()
router.register(r'playbooks', OrchestrationViewSet, basename='playbooks')

urlpatterns = [
    path('', include(router.urls)),
]
