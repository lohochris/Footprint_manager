from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChannelViewSet,
    ConnectionViewSet,
    SubscriptionViewSet,
    PresenceViewSet,
    StreamAuditViewSet
)

router = DefaultRouter()
router.register(r'channels', ChannelViewSet, basename='channels')
router.register(r'connections', ConnectionViewSet, basename='connections')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register(r'presence', PresenceViewSet, basename='presence')
router.register(r'audit', StreamAuditViewSet, basename='audit')

urlpatterns = [
    path('', include(router.urls)),
]
