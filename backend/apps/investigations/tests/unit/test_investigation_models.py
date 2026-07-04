from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Organization
from backend.apps.investigations.models import (
    Investigation,
    InvestigationMember,
    InvestigationTarget,
    EvidenceReference,
    InvestigationTimelineEvent,
    InvestigationComment,
    InvestigationStatus,
    InvestigationPriority,
    InvestigationType,
    InvestigationClassification,
    TimelineEventType,
    TargetType,
    EvidenceReferenceType,
    InvestigationMemberRole,
    PermissionLevel,
)

User = get_user_model()


class InvestigationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass")
        self.org1 = Organization.objects.create(name="Org 1", slug="org-1", owner=self.user)
        self.org2 = Organization.objects.create(name="Org 2", slug="org-2", owner=self.user)

    def test_investigation_creation_and_defaults(self):
        inv = Investigation.objects.create(
            case_number="CASE-001",
            title="Test Investigation",
            organization=self.org1,
            owner=self.user,
        )
        assert inv.status == InvestigationStatus.DRAFT
        assert inv.priority == InvestigationPriority.MEDIUM
        assert inv.investigation_type == InvestigationType.CUSTOM
        assert inv.classification == InvestigationClassification.PUBLIC
        assert inv.is_archived is False
        assert inv.is_deleted is False

    def test_case_number_uniqueness_within_org(self):
        Investigation.objects.create(
            case_number="CASE-DUPLICATE",
            title="Inv 1",
            organization=self.org1,
            owner=self.user,
        )
        # Creating same case number in different org is allowed
        Investigation.objects.create(
            case_number="CASE-DUPLICATE",
            title="Inv 2",
            organization=self.org2,
            owner=self.user,
        )

        # Creating same case number in SAME org raises IntegrityError
        with pytest.raises(IntegrityError):
            Investigation.objects.create(
                case_number="CASE-DUPLICATE",
                title="Inv 3",
                organization=self.org1,
                owner=self.user,
            )

    def test_soft_delete_and_restore(self):
        inv = Investigation.objects.create(
            case_number="CASE-002",
            title="Delete Me",
            organization=self.org1,
            owner=self.user,
        )
        assert inv.is_deleted is False
        assert inv.deleted_at is None

        inv.soft_delete()
        assert inv.is_deleted is True
        assert inv.deleted_at is not None

        inv.restore()
        assert inv.is_deleted is False
        assert inv.deleted_at is None

    def test_metadata_validation(self):
        inv = Investigation(
            case_number="CASE-003",
            title="Metadata Test",
            organization=self.org1,
            owner=self.user,
            metadata={
                "ai_processed": True,
                "confidence_score": 0.85,
                "tags": ["critical", "malware"],
            }
        )
        inv.full_clean()

        # Invalid ai_processed type
        inv.metadata = {"ai_processed": "yes"}
        with pytest.raises(ValidationError) as excinfo:
            inv.full_clean()
        assert "ai_processed must be a boolean" in str(excinfo.value)

        # Invalid confidence_score range
        inv.metadata = {"confidence_score": 1.5}
        with pytest.raises(ValidationError) as excinfo:
            inv.full_clean()
        assert "confidence_score must be between 0.0 and 1.0" in str(excinfo.value)

        # Invalid tags type
        inv.metadata = {"tags": "not-a-list"}
        with pytest.raises(ValidationError) as excinfo:
            inv.full_clean()
        assert "tags must be a list" in str(excinfo.value)

    def test_target_confidence_validation(self):
        inv = Investigation.objects.create(
            case_number="CASE-004",
            title="Target Test",
            organization=self.org1,
            owner=self.user,
        )

        target = InvestigationTarget(
            investigation=inv,
            target_type=TargetType.IP_ADDRESS,
            display_name="192.168.1.1",
            confidence=Decimal("0.950"),
        )
        target.full_clean()
        target.save()

        # Invalid target: confidence > 1.0
        target2 = InvestigationTarget(
            investigation=inv,
            target_type=TargetType.DOMAIN,
            display_name="example.com",
            confidence=Decimal("1.200"),
        )
        with pytest.raises(ValidationError):
            target2.full_clean()

    def test_timeline_event_immutability(self):
        inv = Investigation.objects.create(
            case_number="CASE-005",
            title="Timeline Test",
            organization=self.org1,
            owner=self.user,
        )
        event = InvestigationTimelineEvent.objects.create(
            investigation=inv,
            event_type=TimelineEventType.CREATED,
            description="Created investigation",
        )

        event.description = "Updated description"
        with pytest.raises(ValidationError) as excinfo:
            event.save()
        assert "Timeline events are immutable" in str(excinfo.value)

    def test_member_uniqueness_constraint(self):
        inv = Investigation.objects.create(
            case_number="CASE-006",
            title="Member Test",
            organization=self.org1,
            owner=self.user,
        )
        InvestigationMember.objects.create(
            investigation=inv,
            user=self.user,
            role=InvestigationMemberRole.COLLABORATOR,
            permission_level=PermissionLevel.READ,
        )
        with pytest.raises(IntegrityError):
            InvestigationMember.objects.create(
                investigation=inv,
                user=self.user,
                role=InvestigationMemberRole.LEAD,
                permission_level=PermissionLevel.ADMIN,
            )
