"""Infrastructure tests for Footprint Manager Sprint 0."""

import pytest


@pytest.mark.django_db
class TestHealthEndpoints:
    def test_health_check_returns_200(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_liveness_check_returns_200(self, api_client):
        response = api_client.get("/health/live/")
        assert response.status_code == 200

    def test_readiness_check_returns_status(self, api_client):
        response = api_client.get("/health/ready/")
        assert response.status_code in (200, 503)
        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert "cache" in data["checks"]


class TestOpenAPI:
    def test_schema_endpoint_returns_200(self, api_client):
        response = api_client.get("/api/schema/")
        assert response.status_code == 200

    def test_swagger_ui_loads(self, api_client):
        response = api_client.get("/api/docs/swagger/")
        assert response.status_code == 200

    def test_redoc_loads(self, api_client):
        response = api_client.get("/api/docs/redoc/")
        assert response.status_code == 200
