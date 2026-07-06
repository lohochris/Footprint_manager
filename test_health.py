import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")
django.setup()

from django.test import RequestFactory
from backend.apps.observability.api.views import HealthViewSet
from backend.apps.accounts.models import User

factory = RequestFactory()
request = factory.get('/api/v1/observability/health/')
# Create a user to bypass IsAuthenticated manually in the view or attach it to request
user = User.objects.first()
if not user:
    user = User.objects.create(email="test@example.com")
# Give the user tenant_id if it's missing
if not hasattr(user, 'tenant_id'):
    user.tenant_id = 'test_tenant'

from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

api_factory = APIRequestFactory()
req = api_factory.get('/api/v1/observability/health/')
force_authenticate(req, user=user)

view = HealthViewSet.as_view({'get': 'list'})
try:
    response = view(req)
    print(response.data)
except Exception:
    import traceback
    traceback.print_exc()
