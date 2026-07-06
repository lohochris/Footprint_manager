import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings.testing")
django.setup()

import traceback
from rest_framework.test import APIRequestFactory, force_authenticate
from backend.apps.accounts.models import User
from backend.apps.organizations.api.views.workspace_viewset import WorkspaceViewSet
from backend.apps.observability.api.views import HealthViewSet, AlertViewSet
from backend.apps.collaboration.api.views import NotificationViewSet

user = User.objects.first()
factory = APIRequestFactory()

print("\n\n=== WORKSPACE ENDPOINT ===")
try:
    request = factory.get('/api/v1/workspaces/default-investigation-workspace/')
    force_authenticate(request, user=user)
    view = WorkspaceViewSet.as_view({'get': 'retrieve'})
    response = view(request, pk='default-investigation-workspace')
    print("Status:", response.status_code)
except Exception:
    traceback.print_exc()

print("\n\n=== HEALTH ENDPOINT ===")
try:
    request = factory.get('/api/v1/observability/health/?workspace=default-investigation-workspace')
    force_authenticate(request, user=user)
    view = HealthViewSet.as_view({'get': 'list'})
    response = view(request)
    print("Status:", response.status_code)
except Exception:
    traceback.print_exc()

print("\n\n=== ALERTS ENDPOINT ===")
try:
    request = factory.get('/api/v1/observability/alerts/')
    force_authenticate(request, user=user)
    view = AlertViewSet.as_view({'get': 'list'})
    response = view(request)
    print("Status:", response.status_code)
except Exception:
    traceback.print_exc()

print("\n\n=== NOTIFICATIONS ENDPOINT ===")
try:
    request = factory.get('/api/v1/collaboration/notifications/?workspace=default-investigation-workspace')
    force_authenticate(request, user=user)
    view = NotificationViewSet.as_view({'get': 'list'})
    response = view(request)
    print("Status:", response.status_code)
except Exception:
    traceback.print_exc()
