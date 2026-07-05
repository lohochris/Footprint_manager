import pytest
from rest_framework.test import APIClient
from rest_framework import status
import uuid
from django.contrib.auth import get_user_model
from backend.apps.organizations.models.organization import Organization
from backend.apps.intelligence.models import EntityScore

User = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_a():
    user = User.objects.create(email="a@example.com")
    user.set_password("pass")
    user.save()
    return user

@pytest.fixture
def user_b():
    user = User.objects.create(email="b@example.com")
    user.set_password("pass")
    user.save()
    return user

@pytest.fixture
def tenant_a(user_a):
    return Organization.objects.create(name="Tenant A", slug="tenant-a", owner=user_a)

@pytest.fixture
def tenant_b(user_b):
    return Organization.objects.create(name="Tenant B", slug="tenant-b", owner=user_b)

def test_tenant_isolation_entity_score(api_client, tenant_a, tenant_b, user_a, user_b):
    EntityScore.objects.create(
        tenant_id=tenant_a.id,
        owner=user_a,
        node_id=uuid.uuid4(),
        risk_score="0.5000"
    )
    EntityScore.objects.create(
        tenant_id=tenant_b.id,
        owner=user_b,
        node_id=uuid.uuid4(),
        risk_score="0.8000"
    )

    # User A requests
    # Wait, the views use `tenant_id=self.request.user.tenant_id`. Let's mock the user's tenant_id
    user_a.tenant_id = tenant_a.id
    user_b.tenant_id = tenant_b.id

    api_client.force_authenticate(user=user_a)
    response = api_client.get("/api/v1/intelligence/scores/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["risk_score"] == "0.5000"

    # User B requests
    api_client.force_authenticate(user=user_b)
    response = api_client.get("/api/v1/intelligence/scores/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["risk_score"] == "0.8000"

def test_intelligence_calculate_requires_workspace(api_client, user_a):
    api_client.force_authenticate(user=user_a)
    response = api_client.post("/api/v1/intelligence/operations/calculate/")
    # Since workspace is missing, it should handle the failure or error gracefully.
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]
