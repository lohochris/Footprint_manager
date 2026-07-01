import pytest
from django.test import TestCase
from apps.organizations.services.invitation_service import InvitationService
from apps.organizations.models import Organization, OrganizationMember
from apps.users.models import User

class InvitationServiceTests(TestCase):
    def setUp(self):
        # Create minimal organization and user fixtures
        self.org = Organization.objects.create(name="Test Org", slug="test-org")
        self.inviter = User.objects.create_user(username="inviter", email="inviter@example.com", password="pass")
        self.invitee = User.objects.create_user(username="invitee", email="invitee@example.com", password="pass")

    def test_invite_user_returns_dict(self):
        result = InvitationService.invite_user(self.org, "new@example.com", self.inviter)
        assert isinstance(result, dict)
        assert "invitation" in result and "token" in result

    def test_accept_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "accept@example.com", self.inviter)
        token = creation["token"]
        result = InvitationService.accept_invitation(token, self.invitee)
        assert result == {"status": "success"}

    def test_reject_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "reject@example.com", self.inviter)
        token = creation["token"]
        result = InvitationService.reject_invitation(token, self.invitee)
        assert result == {"status": "success"}

    def test_cancel_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "cancel@example.com", self.inviter)
        token = creation["token"]
        result = InvitationService.cancel_invitation(token, self.inviter)
        assert result == {"status": "success"}

    def test_resend_invitation_returns_success(self):
        creation = InvitationService.invite_user(self.org, "resend@example.com", self.inviter)
        token = creation["token"]
        result = InvitationService.resend_invitation(token, self.inviter)
        assert result == {"status": "success"}

    def test_expire_stale_invitations_returns_dict(self):
        result = InvitationService.expire_stale_invitations()
        assert isinstance(result, dict)
        assert "expired_count" in result
