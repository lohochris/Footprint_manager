import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")
django.setup()

import traceback
from django.test import RequestFactory
from rest_framework.test import APIClient
from backend.apps.accounts.models import User
from backend.apps.organizations.models import Organization, OrganizationMember

# Grab the first user setup by setup_dev_env
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
    print("\n=============================================")
    print(f"Testing Endpoint: {endpoint}")
    print("=============================================")
    try:
        response = client.get(endpoint)
        print(f"Status Code: {response.status_code}")
        if response.status_code >= 500 or response.status_code == 400 or response.status_code == 403:
            print("Response Data:", response.content)
    except Exception:
        print(f"Exception caught while calling {endpoint}")
        traceback.print_exc()

