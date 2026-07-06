import pytest
import uuid
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from backend.apps.ai_assistant.models import AssistantSession

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create(username="tenant_user")

def test_tenant_isolation_sessions(user):
    # Setup
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    session_a = AssistantSession.objects.create(tenant_id=tenant_a, owner=user, title="Tenant A Session")
    session_b = AssistantSession.objects.create(tenant_id=tenant_b, owner=user, title="Tenant B Session")

    # Simulate middleware injecting tenant_id for Tenant A
    class MockRequestAuth:
        def __init__(self, tenant_id):
            self.tenant_id = tenant_id

    # To test the ViewSet, we can mock the request tenant_id or just test the logic directly
    from backend.apps.ai_assistant.api.views import AssistantSessionViewSet
    from rest_framework.request import Request
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.get('/api/v1/ai/sessions/')
    # Inject tenant A
    request.tenant_id = tenant_a

    view = AssistantSessionViewSet.as_view({'get': 'list'})
    response = view(request)

    assert response.status_code == 200
    # Should only return 1 session (Tenant A)
    assert len(response.data) == 1
    assert response.data[0]['id'] == str(session_a.id)

    # Inject tenant B
    request_b = factory.get('/api/v1/ai/sessions/')
    request_b.tenant_id = tenant_b
    response_b = view(request_b)

    assert len(response_b.data) == 1
    assert response_b.data[0]['id'] == str(session_b.id)

def test_tenant_isolation_chat_endpoint(user):
    # Testing that a tenant cannot chat on another tenant's session
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    session_b = AssistantSession.objects.create(tenant_id=tenant_b, owner=user)

    from backend.apps.ai_assistant.api.views import AssistantSessionViewSet
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.post(f'/api/v1/ai/sessions/{session_b.id}/chat/', data={"message": "hello"}, content_type="application/json")
    request.tenant_id = tenant_a  # Request is made by Tenant A

    view = AssistantSessionViewSet.as_view({'post': 'chat'})

    # This should 404 because the get_queryset filters by request.tenant_id
    from django.http import Http404
    with pytest.raises(Http404):
        view(request, pk=session_b.id)
