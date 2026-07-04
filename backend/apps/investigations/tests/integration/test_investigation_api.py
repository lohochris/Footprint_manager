import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from backend.apps.organizations.models import Organization, OrganizationMember, Workspace
from backend.apps.investigations.models import (
    Investigation,
    InvestigationMember,
    InvestigationMemberRole,
    InvestigationStatus,
    InvestigationPriority,
    InvestigationType,
    InvestigationClassification,
    InvestigationTarget,
    EvidenceReference,
    InvestigationComment,
    InvestigationTimelineEvent,
    PermissionLevel,
)
from backend.apps.investigations.services.investigation_service import InvestigationService

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner_user(db):
    return User.objects.create_user(
        username="owner", email="owner@example.com", password="password123"
    )


@pytest.fixture
def lead_user(db):
    return User.objects.create_user(
        username="lead", email="lead@example.com", password="password123"
    )


@pytest.fixture
def analyst_user(db):
    return User.objects.create_user(
        username="analyst", email="analyst@example.com", password="password123"
    )


@pytest.fixture
def external_user(db):
    return User.objects.create_user(
        username="external", email="external@example.com", password="password123"
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="super", email="super@example.com", password="password123"
    )


@pytest.fixture
def org(db, owner_user, lead_user, analyst_user):
    organization = Organization.objects.create(name="FM Org", slug="fm-org", owner=owner_user)
    OrganizationMember.objects.create(organization=organization, user=owner_user, role="owner", status="active")
    OrganizationMember.objects.create(organization=organization, user=lead_user, role="admin", status="active")
    OrganizationMember.objects.create(organization=organization, user=analyst_user, role="analyst", status="active")
    return organization


@pytest.fixture
def other_org(db, external_user):
    organization = Organization.objects.create(name="Other Org", slug="other-org", owner=external_user)
    OrganizationMember.objects.create(organization=organization, user=external_user, role="owner", status="active")
    return organization


@pytest.fixture
def ws(db, org):
    return Workspace.objects.create(name="FM Workspace", slug="fm-ws", organization=org)


@pytest.fixture
def investigation(db, org, owner_user, ws):
    # Setup initial active investigation owned by owner_user using the service layer
    return InvestigationService.create_investigation(
        user=owner_user,
        organization=org,
        workspace=ws,
        data={
            "title": "Brute Force Alert",
            "description": "Brute force login failures",
            "priority": "medium",
            "investigation_type": "cybercrime",
            "classification": "confidential",
        }
    )


def get_auth_client(user):
    client = APIClient()
    token = AccessToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
class TestInvestigationAPI:
    """Integration test suite for the REST API endpoints of Investigations context."""

    def test_unauthenticated_requests_fail(self, api_client, org, investigation):
        endpoints = [
            ("/api/v1/investigations/", "GET"),
            ("/api/v1/investigations/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/", "GET"),
            (f"/api/v1/investigations/{investigation.id}/", "PATCH"),
            (f"/api/v1/investigations/{investigation.id}/", "DELETE"),
            (f"/api/v1/investigations/{investigation.id}/assign/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/status/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/archive/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/restore/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/targets/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/evidence/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/comments/", "POST"),
            (f"/api/v1/investigations/{investigation.id}/timeline/", "GET"),
        ]
        for url, method in endpoints:
            if method == "GET":
                response = api_client.get(url)
            elif method == "PATCH":
                response = api_client.patch(url, {})
            elif method == "DELETE":
                response = api_client.delete(url)
            else:
                response = api_client.post(url, {})
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_tenant_isolation_prevents_unauthorized_access(self, investigation, other_org, external_user):
        # external_user is from other_org and should not see investigation in org
        client = get_auth_client(external_user)

        # Detail view should return 404 (due to get_queryset scoping to tenant)
        response = client.get(f"/api/v1/investigations/{investigation.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # List view should return empty list
        response = client.get("/api/v1/investigations/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_create_investigation_success(self, lead_user, org, ws):
        client = get_auth_client(lead_user)
        payload = {
            "title": "New Cyber Threat Campaign",
            "description": "Investigation into phishing emails",
            "workspace": str(ws.id),
            "investigation_type": "cybercrime",
            "priority": "high",
            "classification": "confidential",
            "tags": ["phishing", "threat-intel"],
            "metadata": {"malicious_link": "http://evil.com"},
        }
        response = client.post("/api/v1/investigations/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Cyber Threat Campaign"
        assert response.data["case_number"] is not None

        # Check in DB
        inv = Investigation.objects.get(id=response.data["id"])
        assert inv.owner == lead_user
        assert inv.organization == org

    def test_create_investigation_malformed_request(self, lead_user, org):
        client = get_auth_client(lead_user)

        # Missing required title
        payload = {
            "description": "No title",
            "priority": "invalid-priority-value",
        }
        response = client.post("/api/v1/investigations/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data or "title" in str(response.data)
        assert "priority" in response.data or "priority" in str(response.data)

    def test_retrieve_investigation_detail(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)
        response = client.get(f"/api/v1/investigations/{investigation.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == investigation.title
        assert "members" in response.data
        assert "targets" in response.data
        assert "evidence_references" in response.data
        assert "comments" in response.data
        assert "timeline_events" in response.data

    def test_update_investigation_success(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)
        payload = {
            "title": "Phishing Alert Refined",
            "priority": "low",
        }
        response = client.patch(f"/api/v1/investigations/{investigation.id}/", payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Phishing Alert Refined"
        assert response.data["priority"] == "low"

    def test_soft_delete_investigation(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)
        response = client.delete(f"/api/v1/investigations/{investigation.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Investigation is marked as deleted
        investigation.refresh_from_db()
        assert investigation.is_deleted is True

    def test_status_transitions_valid_and_invalid(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)

        # Valid transition: draft -> active
        response = client.post(f"/api/v1/investigations/{investigation.id}/status/", {"status": "active"})
        assert response.status_code == status.HTTP_200_OK
        investigation.refresh_from_db()
        assert investigation.status == InvestigationStatus.ACTIVE

        # Invalid transition: active -> draft (raises validation error)
        response = client.post(f"/api/v1/investigations/{investigation.id}/status/", {"status": "draft"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_assign_investigators(self, owner_user, org, investigation, analyst_user):
        client = get_auth_client(owner_user)
        payload = {"investigator_ids": [analyst_user.id]}
        response = client.post(f"/api/v1/investigations/{investigation.id}/assign/", payload, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Verify in DB
        assert InvestigationMember.objects.filter(
            investigation=investigation, user=analyst_user, active=True
        ).exists()

    def test_archive_and_restore_operations(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)

        # Archive
        response = client.post(f"/api/v1/investigations/{investigation.id}/archive/")
        assert response.status_code == status.HTTP_200_OK
        investigation.refresh_from_db()
        assert investigation.is_archived is True
        assert investigation.status == InvestigationStatus.ARCHIVED

        # Restore
        response = client.post(f"/api/v1/investigations/{investigation.id}/restore/")
        assert response.status_code == status.HTTP_200_OK
        investigation.refresh_from_db()
        assert investigation.is_archived is False
        assert investigation.status == InvestigationStatus.ACTIVE

    def test_targets_crud_via_api(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)

        # POST target
        payload = {
            "target_type": "ip_address",
            "display_name": "198.51.100.42",
            "confidence": "0.950",
            "notes": "Suspect command & control IP",
        }
        response = client.post(f"/api/v1/investigations/{investigation.id}/targets/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["display_name"] == "198.51.100.42"

        # GET targets list
        response = client.get(f"/api/v1/investigations/{investigation.id}/targets/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["display_name"] == "198.51.100.42"

    def test_evidence_references_crud_via_api(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)

        # POST evidence
        payload = {
            "reference_type": "url",
            "source": "VirusTotal Report",
            "uri": "https://virustotal.com/report/123",
            "summary": "Forensic scan results showing high threat score",
        }
        response = client.post(f"/api/v1/investigations/{investigation.id}/evidence/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["source"] == "VirusTotal Report"

        # GET evidence list
        response = client.get(f"/api/v1/investigations/{investigation.id}/evidence/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["source"] == "VirusTotal Report"

    def test_comments_crud_via_api(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)

        # POST comment
        payload = {
            "rich_content": "Reviewed the logs and verified target IP coordinates."
        }
        response = client.post(f"/api/v1/investigations/{investigation.id}/comments/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["rich_content"] == "Reviewed the logs and verified target IP coordinates."
        assert response.data["author_username"] == "owner"

        # GET comments list
        response = client.get(f"/api/v1/investigations/{investigation.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["rich_content"] == "Reviewed the logs and verified target IP coordinates."

    def test_timeline_event_retrieval(self, owner_user, org, investigation):
        client = get_auth_client(owner_user)

        # Timeline has at least the CREATED event from service setup
        response = client.get(f"/api/v1/investigations/{investigation.id}/timeline/")
        assert response.status_code == status.HTTP_200_OK
        # Since we resolved through direct selector, we expect events
        assert len(response.data) >= 1

    def test_filtering_and_pagination(self, lead_user, org, ws):
        client = get_auth_client(lead_user)
        # Create 3 investigations
        for i in range(3):
            Investigation.objects.create(
                case_number=f"FM-ORG-2026-000{i+2}",
                title=f"Bulk Investigation {i}",
                organization=org,
                workspace=ws,
                owner=lead_user,
                status=InvestigationStatus.DRAFT if i < 2 else InvestigationStatus.ACTIVE,
                priority=InvestigationPriority.HIGH if i == 0 else InvestigationPriority.LOW,
            )

        # Test filter by status=draft
        response = client.get("/api/v1/investigations/?status=draft")
        assert response.status_code == status.HTTP_200_OK
        # Standard results set pagination: the results are under results key
        drafts = [item for item in response.data["results"] if item["status"] == "draft"]
        assert len(drafts) >= 2

        # Test filter by priority=high
        response = client.get("/api/v1/investigations/?priority=high")
        assert response.status_code == status.HTTP_200_OK
        highs = [item for item in response.data["results"] if item["priority"] == "high"]
        assert len(highs) >= 1

        # Test pagination: default limit is 20, let's request page_size=2
        response = client.get("/api/v1/investigations/?page_size=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_openapi_schema_endpoint_available(self, lead_user, org):
        client = get_auth_client(lead_user)
        response = client.get("/api/schema/")
        # drf_spectacular schema endpoint is configured in base.py/urls.py
        assert response.status_code == status.HTTP_200_OK
