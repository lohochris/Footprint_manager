import pytest
from django.test import TestCase
from backend.apps.organizations.services.invitation_service import InvitationService
from backend.apps.organizations.models import Organization, OrganizationMember
from django.contrib.auth import get_user_model
User = get_user_model()

class InvitationServiceTests(TestCase):
    def setUp(self):
        # Create minimal organization and user fixtures
        self.inviter = User.objects.create_user(username="inviter", email="inviter@example.com", password="pass")
        self.invitee = User.objects.create_user(username="invitee", email="invitee@example.com", password="pass")
        self.org = Organization.objects.create(name="Test Org", slug="test-org", owner=self.inviter)

    def test_invite_user_returns_dict(self):
        result = InvitationService.invite_user(self.org, "new@example.com", self.inviter)
        assert result.success is True
        assert isinstance(result.data, dict)
        assert "invitation" in result.data and "token" in result.data

    def test_accept_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "accept@example.com", self.inviter)
        assert creation.success is True
        token = creation.data["token"]
        result = InvitationService.accept_invitation(token, self.invitee)
        assert result.success is True
        assert result.data == {"status": "success"}

    def test_reject_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "reject@example.com", self.inviter)
        assert creation.success is True
        token = creation.data["token"]
        result = InvitationService.reject_invitation(token, self.invitee)
        assert result.success is True
        assert result.data == {"status": "success"}

    def test_cancel_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "cancel@example.com", self.inviter)
        assert creation.success is True
        token = creation.data["token"]
        result = InvitationService.cancel_invitation(token, self.inviter)
        assert result.success is True
        assert result.data == {"status": "success"}

    def test_resend_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "resend@example.com", self.inviter)
        assert creation.success is True
        token = creation.data["token"]
        result = InvitationService.resend_invitation(token, self.inviter)
        assert result.success is True
        assert result.data == {"status": "success"}

    def test_expire_stale_invitations_returns_dict(self):
        result = InvitationService.expire_stale_invitations()
        assert result.success is True
        assert isinstance(result.data, dict)
        assert "expired_count" in result.data
