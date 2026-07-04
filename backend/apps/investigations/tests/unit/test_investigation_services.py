import pytest
from unittest.mock import patch
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Organization, Workspace
from backend.apps.investigations.models import (
    Investigation,
    InvestigationMember,
    InvestigationMemberRole,
    InvestigationStatus,
    InvestigationTimelineEvent,
    TimelineEventType,
    PermissionLevel,
)
from backend.apps.investigations.services.investigation_service import InvestigationService

User = get_user_model()


class InvestigationServiceTests(TestCase):
    def setUp(self):
        # Create user fixtures
        self.owner = User.objects.create_user(username="org_owner", email="owner@example.com", password="pass")
        self.lead = User.objects.create_user(username="lead_user", email="lead@example.com", password="pass")
        self.analyst = User.objects.create_user(username="analyst_user", email="analyst@example.com", password="pass")
        self.unauthorized_user = User.objects.create_user(username="unauth_user", email="unauth@example.com", password="pass")

        # Create organizations and workspace
        self.org = Organization.objects.create(name="FM Org", slug="fm-org", owner=self.owner)
        self.other_org = Organization.objects.create(name="Other Org", slug="other-org", owner=self.owner)
        self.workspace = Workspace.objects.create(name="FM Workspace", slug="fm-ws", organization=self.org)
        self.other_workspace = Workspace.objects.create(name="Other WS", slug="other-ws", organization=self.other_org)

        # Register users as active members of the primary organization
        from backend.apps.organizations.models import OrganizationMember
        OrganizationMember.objects.create(organization=self.org, user=self.owner, status="active")
        OrganizationMember.objects.create(organization=self.org, user=self.lead, status="active")
        OrganizationMember.objects.create(organization=self.org, user=self.analyst, status="active")
        # Note: unauthorized_user is not in self.org!

    def test_create_investigation_success(self):
        data = {
            "title": "Threat Investigation",
            "description": "Suspicious login behavior detected",
        }
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data=data,
        )
        assert inv is not None
        assert inv.title == "Threat Investigation"
        assert inv.case_number.startswith("FM-ORG-")

        # Confirm owner membership created
        member = InvestigationMember.objects.get(investigation=inv, user=self.lead)
        assert member.role == InvestigationMemberRole.OWNER
        assert member.permission_level == PermissionLevel.ADMIN

        # Confirm timeline event registered
        timeline = InvestigationTimelineEvent.objects.filter(investigation=inv)
        assert timeline.count() == 1
        assert timeline.first().event_type == TimelineEventType.CREATED

    def test_mismatched_workspace_tenancy_fails(self):
        data = {"title": "Mismatched Tenancy"}
        with pytest.raises(ValidationError) as excinfo:
            # self.other_workspace belongs to self.other_org, not self.org!
            InvestigationService.create_investigation(
                user=self.lead,
                organization=self.org,
                workspace=self.other_workspace,
                data=data,
            )
        assert "does not belong to organization" in str(excinfo.value)

    def test_unauthorized_user_creation_fails(self):
        data = {"title": "Unauthorized Create"}
        with pytest.raises(ValidationError) as excinfo:
            # self.unauthorized_user is not in self.org
            InvestigationService.create_investigation(
                user=self.unauthorized_user,
                organization=self.org,
                workspace=self.workspace,
                data=data,
            )
        assert "is not an active member" in str(excinfo.value)

    def test_update_investigation_by_lead_success(self):
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Original Title"},
        )

        updated = InvestigationService.update_investigation(
            user=self.lead,
            investigation=inv,
            data={"title": "Updated Title"},
        )
        assert updated.title == "Updated Title"

    def test_unauthorized_update_fails(self):
        # Create investigation owned by lead
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Secure Title"},
        )

        # analyst_user is not a member of the investigation yet
        with pytest.raises(PermissionDenied):
            InvestigationService.update_investigation(
                user=self.analyst,
                investigation=inv,
                data={"title": "Hack Attempt"},
            )

    def test_assign_investigators_success(self):
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Team Work"},
        )

        # Add analyst to the investigation
        InvestigationService.assign_investigators(
            user=self.lead,
            investigation=inv,
            investigator_ids=[self.analyst.pk],
        )

        member = InvestigationMember.objects.get(investigation=inv, user=self.analyst)
        assert member.role == InvestigationMemberRole.INVESTIGATOR
        assert member.active is True

        # Timeline event verification
        timeline = InvestigationTimelineEvent.objects.filter(investigation=inv)
        assert timeline.filter(event_type=TimelineEventType.MEMBER_ADDED).exists()

    def test_change_status_success_and_transitions(self):
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Status Shifts"},
        )
        assert inv.status == InvestigationStatus.DRAFT

        # Draft -> Active is allowed
        InvestigationService.change_status(self.lead, inv, InvestigationStatus.ACTIVE)
        inv.refresh_from_db()
        assert inv.status == InvestigationStatus.ACTIVE

        # Active -> Draft is NOT allowed
        with pytest.raises(ValidationError):
            InvestigationService.change_status(self.lead, inv, InvestigationStatus.DRAFT)

    def test_completed_status_sets_closed_at(self):
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Resolution Test"},
        )
        InvestigationService.change_status(self.lead, inv, InvestigationStatus.ACTIVE)
        assert inv.closed_at is None

        # Active -> Completed
        InvestigationService.change_status(self.lead, inv, InvestigationStatus.COMPLETED)
        inv.refresh_from_db()
        assert inv.status == InvestigationStatus.COMPLETED
        assert inv.closed_at is not None

    def test_archive_and_dedicated_restore(self):
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Archive Verification"},
        )

        # Draft -> Archived
        InvestigationService.archive(self.lead, inv)
        inv.refresh_from_db()
        assert inv.is_archived is True
        assert inv.status == InvestigationStatus.ARCHIVED

        # Standard status transition from archived is blocked (e.g. to active)
        with pytest.raises(ValidationError):
            InvestigationService.change_status(self.lead, inv, InvestigationStatus.ACTIVE)

        # Dedicated administrative restore succeeds
        InvestigationService.restore_investigation(self.lead, inv)
        inv.refresh_from_db()
        assert inv.is_archived is False
        assert inv.status == InvestigationStatus.ACTIVE

    def test_transfer_ownership(self):
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Valuable Assets"},
        )
        assert inv.owner == self.lead

        # Transfer lead -> analyst
        InvestigationService.transfer_ownership(self.lead, inv, self.analyst)
        inv.refresh_from_db()
        assert inv.owner == self.analyst

        # Previous owner (lead) demoted to investigator
        old_owner_member = InvestigationMember.objects.get(investigation=inv, user=self.lead)
        assert old_owner_member.role == InvestigationMemberRole.INVESTIGATOR

        # New owner has owner role
        new_owner_member = InvestigationMember.objects.get(investigation=inv, user=self.analyst)
        assert new_owner_member.role == InvestigationMemberRole.OWNER

    def test_unauthorized_ownership_transfer_fails(self):
        inv = InvestigationService.create_investigation(
            user=self.lead,
            organization=self.org,
            workspace=self.workspace,
            data={"title": "Vulnerable Ownership"},
        )

        # analyst attempts to transfer ownership of lead's investigation
        with pytest.raises(PermissionDenied):
            InvestigationService.transfer_ownership(self.analyst, inv, self.owner)

    def test_transaction_rollback_on_timeline_failure(self):
        # We mock timeline event save to crash, verifying that the entire transaction rolls back
        data = {"title": "Atomic Security Rollback"}

        with patch.object(InvestigationTimelineEvent.objects, 'create', side_effect=Exception("Timeline database failure")):
            with pytest.raises(Exception) as excinfo:
                InvestigationService.create_investigation(
                    user=self.lead,
                    organization=self.org,
                    workspace=self.workspace,
                    data=data,
                )
            assert "Timeline database failure" in str(excinfo.value)

        # Verify that absolutely no Investigation or InvestigationMember was created in the database
        assert not Investigation.objects.filter(title="Atomic Security Rollback").exists()
        assert not InvestigationMember.objects.filter(user=self.lead).exists()
