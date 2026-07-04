import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from backend.apps.organizations.models import Organization, OrganizationMember, Workspace
from backend.apps.evidence.models import Evidence
from backend.apps.evidence.services import EvidenceService

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


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
def org(db, lead_user, analyst_user):
    organization = Organization.objects.create(name="FM Org", slug="fm-org", owner=lead_user)
    OrganizationMember.objects.create(organization=organization, user=lead_user, role="owner", status="active")
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


def authenticate_client(client, user):
    client.force_authenticate(user=user)


# ===========================================================================
# API INTEGRATION TESTS
# ===========================================================================

def test_evidence_create_success(api_client, org, ws, lead_user):
    authenticate_client(api_client, lead_user)
    file_content = b"evidence file data"
    file_obj = SimpleUploadedFile("phishing_header.txt", file_content)

    data = {
        "title": "Email Headers",
        "description": "Suspicious headers",
        "classification": "restricted",
        "workspace": str(ws.id),
        "file": file_obj,
    }

    response = api_client.post("/api/v1/evidence/", data, format="multipart")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Email Headers"
    assert response.data["status"] == "uploaded"
    assert response.data["current_custodian_username"] == "lead"


def test_evidence_list_and_retrieve_success(api_client, org, ws, lead_user):
    # Upload evidence first
    file_obj = SimpleUploadedFile("logs.txt", b"Log data")
    evidence = EvidenceService.upload_evidence(
        user=lead_user,
        organization=org,
        workspace_id=ws.id,
        title="Server Logs",
        description="Detail",
        classification="restricted",
        file_obj=file_obj,
    )

    authenticate_client(api_client, lead_user)

    # Test list
    response = api_client.get("/api/v1/evidence/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == "Server Logs"

    # Test retrieve
    response = api_client.get(f"/api/v1/evidence/{evidence.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Server Logs"


def test_evidence_tenant_isolation(api_client, org, other_org, ws, lead_user, external_user):
    # Create evidence in Org A
    file_obj = SimpleUploadedFile("logs.txt", b"Log data")
    evidence = EvidenceService.upload_evidence(
        user=lead_user,
        organization=org,
        workspace_id=ws.id,
        title="Tenant A Evidence",
        description="Detail",
        classification="restricted",
        file_obj=file_obj,
    )

    # Attempt to retrieve from Org B user
    authenticate_client(api_client, external_user)
    response = api_client.get(f"/api/v1/evidence/{evidence.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_evidence_custody_transfer_success(api_client, org, ws, lead_user, analyst_user):
    # Upload evidence
    file_obj = SimpleUploadedFile("log.txt", b"some logs")
    evidence = EvidenceService.upload_evidence(
        user=lead_user,
        organization=org,
        workspace_id=ws.id,
        title="Original Logs",
        description="Original",
        classification="restricted",
        file_obj=file_obj,
    )

    # Lead user (custodian) transfers to analyst
    authenticate_client(api_client, lead_user)
    data = {
        "new_custodian_id": analyst_user.id,
        "notes": "Handing off to analyst",
    }
    response = api_client.post(f"/api/v1/evidence/{evidence.id}/transfer/", data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["current_custodian_username"] == "analyst"

    # Attempt another transfer by lead user (should fail due to custodian lock)
    data2 = {
        "new_custodian_id": lead_user.id,
        "notes": "Trying to take back",
    }
    response2 = api_client.post(f"/api/v1/evidence/{evidence.id}/transfer/", data2)
    assert response2.status_code == status.HTTP_403_FORBIDDEN


def test_evidence_download_lock(api_client, org, ws, lead_user, analyst_user):
    # Upload evidence
    file_obj = SimpleUploadedFile("log.txt", b"some logs")
    evidence = EvidenceService.upload_evidence(
        user=lead_user,
        organization=org,
        workspace_id=ws.id,
        title="Secure Data",
        description="Secure",
        classification="restricted",
        file_obj=file_obj,
    )

    # Custodian (lead_user) can request download URL
    authenticate_client(api_client, lead_user)
    response = api_client.get(f"/api/v1/evidence/{evidence.id}/download/")
    assert response.status_code == status.HTTP_200_OK
    assert "download_url" in response.data

    # Non-custodian (analyst_user) is blocked by custodian lock
    authenticate_client(api_client, analyst_user)
    response2 = api_client.get(f"/api/v1/evidence/{evidence.id}/download/")
    assert response2.status_code == status.HTTP_403_FORBIDDEN


def test_evidence_verify_integrity(api_client, org, ws, lead_user):
    file_obj = SimpleUploadedFile("log.txt", b"some logs")
    evidence = EvidenceService.upload_evidence(
        user=lead_user,
        organization=org,
        workspace_id=ws.id,
        title="Check Integrity",
        description="Verify",
        classification="restricted",
        file_obj=file_obj,
    )

    authenticate_client(api_client, lead_user)
    response = api_client.post(f"/api/v1/evidence/{evidence.id}/verify/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["passed"] is True
    assert response.data["status"] == "verified"


def test_evidence_custody_history(api_client, org, ws, lead_user, analyst_user):
    file_obj = SimpleUploadedFile("log.txt", b"some logs")
    evidence = EvidenceService.upload_evidence(
        user=lead_user,
        organization=org,
        workspace_id=ws.id,
        title="History Log",
        description="History",
        classification="restricted",
        file_obj=file_obj,
    )

    authenticate_client(api_client, lead_user)
    response = api_client.get(f"/api/v1/evidence/{evidence.id}/custody-history/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["event_type"] == "taken"


def test_evidence_update_and_delete(api_client, org, ws, lead_user):
    file_obj = SimpleUploadedFile("log.txt", b"some logs")
    evidence = EvidenceService.upload_evidence(
        user=lead_user,
        organization=org,
        workspace_id=ws.id,
        title="To Mutate",
        description="Original",
        classification="restricted",
        file_obj=file_obj,
    )

    authenticate_client(api_client, lead_user)

    # Test PATCH
    response = api_client.patch(f"/api/v1/evidence/{evidence.id}/", {"title": "Updated Mutate"})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Updated Mutate"

    # Test DELETE
    response_del = api_client.delete(f"/api/v1/evidence/{evidence.id}/")
    assert response_del.status_code == status.HTTP_204_NO_CONTENT

    # Verify is_deleted
    evidence.refresh_from_db()
    assert evidence.is_deleted is True


def test_evidence_permissions_unauthorized(api_client, org, ws, external_user):
    # Attempting to list / create without auth
    response = api_client.get("/api/v1/evidence/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Attempting to upload to a workspace of an organization we don't belong to
    authenticate_client(api_client, external_user)
    file_obj = SimpleUploadedFile("logs.txt", b"log contents")
    data = {
        "title": "Email Headers",
        "description": "Suspicious headers",
        "classification": "restricted",
        "workspace": str(ws.id),
        "file": file_obj,
    }
    response_create = api_client.post("/api/v1/evidence/", data, format="multipart")
    # Should fail tenancy check or org membership check
    assert response_create.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST]

