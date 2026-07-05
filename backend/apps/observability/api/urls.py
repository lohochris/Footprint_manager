from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetricsViewSet, HealthViewSet, AlertViewSet, TraceViewSet, DiagnosticViewSet, DashboardViewSet

router = DefaultRouter()
router.register(r'metrics', MetricsViewSet, basename='observability-metrics')
router.register(r'health', HealthViewSet, basename='observability-health')
router.register(r'alerts', AlertViewSet, basename='observability-alerts')
router.register(r'traces', TraceViewSet, basename='observability-traces')
router.register(r'diagnostics', DiagnosticViewSet, basename='observability-diagnostics')
router.register(r'dashboard', DashboardViewSet, basename='observability-dashboard')

# Root URL config for apps.observability included via global config
urlpatterns = [
    path('api/v1/observability/', include(router.urls)),
]
