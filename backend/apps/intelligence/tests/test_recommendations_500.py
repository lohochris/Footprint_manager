import pytest
from rest_framework.test import APIClient
from backend.apps.accounts.models import User

@pytest.mark.django_db
def test_intelligence_recommendations_500():
    client = APIClient()
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(email="test@example.com", password="testpass123")

    client.force_authenticate(user=user)
    response = client.get('/api/v1/intelligence/recommendations/?workspace=test-slug')

    print("STATUS", response.status_code)
    print("DATA", response.data)
