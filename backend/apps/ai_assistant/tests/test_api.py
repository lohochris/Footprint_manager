import pytest
from rest_framework.test import APIClient
from backend.apps.ai_assistant.models import AssistantSession
import uuid

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

def test_create_session(api_client):
    tenant_id = uuid.uuid4()
    # In reality, auth middleware sets this
    # For now, we mock it or just create a session directly to test the model
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create(username="testuser", email="test@example.com")

    session = AssistantSession.objects.create(
        tenant_id=tenant_id,
        workspace_id=None,
        owner=user,
        title="Test Chat",
    )
    assert session.title == "Test Chat"  # nosec B101
    assert session.status == "active"  # nosec B101

def test_api_urls_resolve(api_client):
    response = api_client.get("/api/v1/ai/sessions/")
    # It should return 401 Unauthorized or 200 depending on auth setup
    assert response.status_code in [200, 401, 403]  # nosec B101
