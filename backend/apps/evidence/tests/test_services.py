from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Organization, Workspace, OrganizationMember
from backend.apps.evidence.models import Evidence, EvidenceCustodyEvent
from backend.apps.evidence.services import EvidenceService
from backend.apps.evidence.selectors import EvidenceSelector

User = get_user_model()


class EvidenceServiceTests(TestCase):
    def setUp(self):
        # Create users
        self.owner = User.objects.create_user(username="org_owner", email="owner@example.com", password="pass")
        self.lead = User.objects.create_user(username="lead_user", email="lead@example.com", password="pass")
        self.analyst = User.objects.create_user(username="analyst_user", email="analyst@example.com", password="pass")
        self.other_user = User.objects.create_user(username="other_user", email="other@example.com", password="pass")

        # Create Organizations
        self.org = Organization.objects.create(name="FM Org", slug="fm-org", owner=self.owner)
        self.other_org = Organization.objects.create(name="Other Org", slug="other-org", owner=self.owner)

        # Create Workspaces
        self.workspace = Workspace.objects.create(name="FM Workspace", slug="fm-ws", organization=self.org)

        # Register users in organization
        OrganizationMember.objects.create(organization=self.org, user=self.owner, status="active")
        OrganizationMember.objects.create(organization=self.org, user=self.lead, status="active")
        OrganizationMember.objects.create(organization=self.org, user=self.analyst, status="active")
        OrganizationMember.objects.create(organization=self.other_org, user=self.other_user, status="active")

    def test_upload_evidence_success(self):
        file_obj = SimpleUploadedFile("logs.txt", b"Forensic log files contents")
        evidence = EvidenceService.upload_evidence(
            user=self.lead,
            organization=self.org,
            workspace_id=self.workspace.id,
            title="Firewall Logs",
            description="Suspicious connection requests",
            classification="restricted",
            file_obj=file_obj,
        )

        assert evidence is not None
        assert evidence.title == "Firewall Logs"
        assert evidence.status == "uploaded"
        assert evidence.current_custodian == self.lead

        # Verify associated File and Version metadata
        assert hasattr(evidence, "file_meta")
        assert evidence.file_meta.original_filename == "logs.txt"
        assert evidence.file_meta.file_size == 27
        assert evidence.file_meta.mime_type == "text/plain"
        assert len(evidence.file_meta.checksum_sha256) == 64

        assert evidence.versions.count() == 1
        assert evidence.versions.first().version_number == 1

        # Check custody events
        events = EvidenceSelector.get_custody_history(evidence)
        assert events.count() == 1
        assert events.first().event_type == "taken"
        assert events.first().holder == self.lead

    def test_upload_evidence_size_limit_fails(self):
        # Setup a mock file with size > 5GB
        file_obj = SimpleUploadedFile("large.txt", b"short content")
        file_obj.size = 6 * 1024 * 1024 * 1024  # Mock size to 6GB

        with self.assertRaises(ValidationError) as context:
            EvidenceService.upload_evidence(
                user=self.lead,
                organization=self.org,
                workspace_id=self.workspace.id,
                title="Large Logs",
                description="Too big",
                classification="restricted",
                file_obj=file_obj,
            )
        assert "exceeds the 5GB limit" in str(context.exception)

    def test_transfer_custody_success(self):
        file_obj = SimpleUploadedFile("payload.bin", b"Malicious payload bytes")
        evidence = EvidenceService.upload_evidence(
            user=self.lead,
            organization=self.org,
            workspace_id=self.workspace.id,
            title="Payload",
            description="Acquired from target",
            classification="restricted",
            file_obj=file_obj,
        )

        # Transfer custody to analyst
        updated_evidence = EvidenceService.transfer_custody(
            user=self.lead,
            organization=self.org,
            evidence=evidence,
            new_custodian=self.analyst,
            notes="Transferred for analysis",
        )

        assert updated_evidence.current_custodian == self.analyst

        # Check custody events
        events = EvidenceSelector.get_custody_history(updated_evidence)
        # 1 taken (upload), 1 released (transfer from), 1 taken (transfer to)
        assert events.count() == 3

        # Verify active custodian lock: analyst is now custodian, lead cannot transfer anymore
        with self.assertRaises(PermissionDenied):
            EvidenceService.transfer_custody(
                user=self.lead,
                organization=self.org,
                evidence=evidence,
                new_custodian=self.owner,
            )

    def test_transfer_custody_tenant_mismatch_fails(self):
        file_obj = SimpleUploadedFile("payload.bin", b"Malicious payload bytes")
        evidence = EvidenceService.upload_evidence(
            user=self.lead,
            organization=self.org,
            workspace_id=self.workspace.id,
            title="Payload",
            description="Acquired",
            classification="restricted",
            file_obj=file_obj,
        )

        # Try transferring to user in another tenant
        with self.assertRaises(ValidationError) as context:
            EvidenceService.transfer_custody(
                user=self.lead,
                organization=self.org,
                evidence=evidence,
                new_custodian=self.other_user,
            )
        assert "same tenant organization" in str(context.exception)

    def test_verify_integrity_success(self):
        file_obj = SimpleUploadedFile("test.txt", b"content")
        evidence = EvidenceService.upload_evidence(
            user=self.lead,
            organization=self.org,
            workspace_id=self.workspace.id,
            title="Test",
            description="Test",
            classification="restricted",
            file_obj=file_obj,
        )

        # Verify integrity
        verified_evidence = EvidenceService.verify_integrity(
            user=self.lead,
            organization=self.org,
            evidence=evidence,
        )
        assert verified_evidence.status == "verified"

        # Modify stored file manually (simulated by mocking storage_provider.read) to trigger checksum failure
        from unittest.mock import patch
        from backend.apps.evidence.services.pipeline_stages import storage_provider

        with patch.object(storage_provider, "read", return_value=b"modified content"):
            # Verify integrity again
            failed_evidence = EvidenceService.verify_integrity(
                user=self.lead,
                organization=self.org,
                evidence=evidence,
            )
        assert failed_evidence.status == "rejected"

    def test_evidence_scanners_exceptions(self):
        from backend.apps.evidence.scanners.base import MalwareScannerError
        with self.assertRaises(MalwareScannerError):
            raise MalwareScannerError("Scan failed")

    def test_evidence_storage_base_abstracts(self):
        from backend.apps.evidence.storage.base import BaseStorageProvider
        # Ensure abstract class is not instantiable
        with self.assertRaises(TypeError):
            BaseStorageProvider()

    def test_evidence_selectors_list_filters(self):
        # Create some dummy evidence items
        file_obj = SimpleUploadedFile("logs.txt", b"Forensic log files contents")
        evidence = EvidenceService.upload_evidence(
            user=self.lead,
            organization=self.org,
            workspace_id=self.workspace.id,
            title="Logs Title",
            description="Descr",
            classification="restricted",
            file_obj=file_obj,
        )

        # Test list with filters
        filters = {
            "status": "uploaded",
            "classification": "restricted",
            "current_custodian_id": self.lead.id,
            "workspace_id": self.workspace.id,
        }
        results, meta = EvidenceSelector.list(
            tenant=self.org,
            filters=filters,
            search="Logs",
            ordering=["created_at"],
            page=1,
            page_size=10,
        )
        assert len(results) == 1
        assert results[0].id == evidence.id
        assert meta["total_items"] == 1

        # Test retrieve
        retrieved = EvidenceSelector.retrieve(self.org, evidence.id)
        assert retrieved.id == evidence.id

