import pytest
import uuid
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from backend.apps.orchestration.models import Playbook, PlaybookVersion

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create(username="api_user")

def test_execute_endpoint(user):
    tenant_id = uuid.uuid4()
    playbook = Playbook.objects.create(tenant_id=tenant_id, name="API PB", owner=user)
    version = PlaybookVersion.objects.create(playbook=playbook, version="1.0", definition={})

    from backend.apps.orchestration.engine.executors import register_executors
    register_executors()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f"/api/v1/orchestration/playbooks/{version.id}/execute/", {"variables": {"target": "foo"}}, format="json")

    assert response.status_code == 201
    assert "id" in response.data
    assert response.data["status"] == "completed"
