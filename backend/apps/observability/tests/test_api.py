import pytest
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_health_live(client):
    response = client.get("/health/live/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "footprint-manager"}

@pytest.mark.django_db
def test_health_ready(client):
    response = client.get("/health/ready/")
    assert response.status_code == 200
    # Allow some variability in checks
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data
