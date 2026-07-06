import pytest
from rest_framework.test import APIClient
from backend.apps.accounts.models import User

@pytest.mark.django_db
def test_all_endpoints():
    user = User.objects.first()
    client = APIClient()
    client.force_authenticate(user=user)

    endpoints = [
        '/api/v1/workspaces/default-investigation-workspace/',
        '/api/v1/observability/health/?workspace=default-investigation-workspace',
        '/api/v1/observability/alerts/',
        '/api/v1/collaboration/notifications/?workspace=default-investigation-workspace',
    ]

    for endpoint in endpoints:
        print(f"\n==== Testing Endpoint: {endpoint} ====")
        try:
            response = client.get(endpoint)
            print(f"Status Code: {response.status_code}")
            if response.status_code >= 400:
                print("Response Data:", response.content)
        except Exception:
            import traceback
            traceback.print_exc()
