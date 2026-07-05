from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, SubscriptionViewSet, IntegrationEventViewSet, WebhookReceiverView, HealthView

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet, basename='integration')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'events', IntegrationEventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/<str:provider_id>/', WebhookReceiverView.as_view(), name='webhook-receiver'),
    path('health/', HealthView.as_view(), name='integration-health'),
]
