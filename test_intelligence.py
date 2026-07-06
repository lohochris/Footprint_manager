import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")
django.setup()

from django.test import RequestFactory
from backend.apps.intelligence.api.views import IntelligenceRecommendationViewSet
from backend.apps.accounts.models import User

factory = RequestFactory()
request = factory.get('/api/v1/intelligence/recommendations/?workspace=default-investigation-workspace&limit=5&ordering=-created_at')
user = User.objects.first()
if not user:
    user = User.objects.create(email="test@example.com")
from backend.apps.organizations.models import Tenant
if not hasattr(user, 'tenant_id') or not user.tenant_id:
    tenant = Tenant.objects.first()
    user.tenant_id = tenant.id
    user.save()

from rest_framework.request import Request
drf_request = Request(request)
drf_request.user = user

view = IntelligenceRecommendationViewSet.as_view({'get': 'list'})
try:
    # Need to give it an actual request context with a user attached
    # request is just WSGIRequest. The view wraps it.
    # Let's attach user to the WSGIRequest
    request.user = user
    response = view(request)
    print("Response status:", response.status_code)
    try:
        response.render()
        print("Response data:", response.content)
    except Exception:
        import traceback
        traceback.print_exc()
except Exception:
    import traceback
    traceback.print_exc()
