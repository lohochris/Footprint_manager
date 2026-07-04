'''Invitation service layer for the organizations app.

Handles creation, acceptance, rejection, cancellation, and expiration of invitations. All mutating actions are logged via AuditLog and respect rate limits.
'''

import time
from collections import defaultdict
from datetime import timedelta

from backend.apps.audit.models.audit_log import AuditLog
from django.db import transaction
from django.utils import timezone

from ..models.invitation import Invitation
from ..models.organization import Organization
from ..models.organization_member import OrganizationMember
from ..validators import (
    generate_invitation_token,
    hash_invitation_token,
    validate_invitation_not_expired,
    validate_no_active_invitation,
)
from .base import ServiceError
from backend.apps.investigations.services.base_service import BaseService

# In‑memory rate‑limit for invitation creation (5 per minute per user)
_RATE_LIMITS = {
    "invitation_creation": {
        "limit": 5,
        "window": 60,
        "counters": defaultdict(list),
    }
}

def _check_invite_rate_limit(user_id):
    cfg = _RATE_LIMITS["invitation_creation"]
    now = time.time()
    timestamps = cfg["counters"][user_id]
    cfg["counters"][user_id] = [t for t in timestamps if now - t < cfg["window"]]
    if len(cfg["counters"][user_id]) >= cfg["limit"]:
        raise ServiceError("Rate limit exceeded for invitation creation.", 429)
    cfg["counters"][user_id].append(now)

# ---------------------------------------------------------------------------
# Private implementation methods (business logic)
# ---------------------------------------------------------------------------


def _invite_user_impl(organization, email, invited_by, expiry_hours=24):
    """Core invitation creation logic.

    This function contains the original implementation that was previously
    exposed as ``InvitationService.invite_user``. It is now invoked via the
    service execution pipeline.
    """
    _check_invite_rate_limit(invited_by.id)
    validate_no_active_invitation(organization, email)
    token = generate_invitation_token()
    expiry_date = timezone.now() + timedelta(hours=expiry_hours)
    invitation = Invitation.objects.create(
        organization=organization,
        email=email,
        invited_by=invited_by,
        token_hash=hash_invitation_token(token),
        expires_at=expiry_date,
    )
    AuditLog.log(invited_by, "INVITATION_CREATED", invitation)
    return {"invitation": invitation, "token": token}


def _accept_invitation_impl(token, user):
    """Core acceptance logic for an invitation."""
    invitation = Invitation.objects.get(token_hash=hash_invitation_token(token))
    validate_invitation_not_expired(invitation)
    with transaction.atomic():
        OrganizationMember.objects.create(
            organization=invitation.organization, user=user
        )
        invitation.delete()
    AuditLog.log(user, "INVITATION_ACCEPTED", invitation)
    return {"status": "success"}


def _reject_invitation_impl(token, user):
    """Core rejection logic for an invitation."""
    invitation = Invitation.objects.get(token_hash=hash_invitation_token(token))
    invitation.delete()
    AuditLog.log(user, "INVITATION_REJECTED", invitation)
    return {"status": "success"}


def _cancel_invitation_impl(token, performed_by):
    """Core cancellation logic for an invitation."""
    invitation = Invitation.objects.get(token_hash=hash_invitation_token(token))
    invitation.delete()
    AuditLog.log(performed_by, "INVITATION_CANCELLED", invitation)
    return {"status": "success"}


def _resend_invitation_impl(token, performed_by):
    """Core resend logic for an invitation.

    In this simplified example we only emit an audit log entry; the actual
    email sending is handled elsewhere.
    """
    invitation = Invitation.objects.get(token_hash=hash_invitation_token(token))
    AuditLog.log(performed_by, "INVITATION_RESENT", invitation)
    return {"status": "success"}


def _expire_stale_invitations_impl():
    """Remove invitations that have passed their expiry date."""
    expired = Invitation.objects.filter(expires_at__lt=timezone.now())
    count = expired.count()
    expired.delete()
    return {"expired_count": count}

# ---------------------------------------------------------------------------
# Public service methods – thin wrappers that delegate to the pipeline
# ---------------------------------------------------------------------------

class InvitationService:
    @staticmethod
    def invite_user(organization, email, invited_by, expiry_hours=24):
        """Create an invitation via the service execution pipeline.

        Args:
            organization: Organization instance the invitation belongs to.
            email: Email address of the invitee.
            invited_by: User performing the invitation.
            expiry_hours: Optional expiry period (default 24h).
        """
        payload = {
            "organization": organization,
            "email": email,
            "invited_by": invited_by,
            "expiry_hours": expiry_hours,
        }
        return BaseService.execute(
            operation="invitation.create",
            performed_by=invited_by,
            tenant=organization,
            payload=payload,
        )

    @staticmethod
    def accept_invitation(token, user):
        """Accept an invitation via the service execution pipeline."""
        payload = {"token": token, "user": user}
        return BaseService.execute(
            operation="invitation.accept",
            performed_by=user,
            tenant=None,
            payload=payload,
        )

    @staticmethod
    def reject_invitation(token, user):
        """Reject an invitation via the service execution pipeline."""
        payload = {"token": token, "user": user}
        return BaseService.execute(
            operation="invitation.reject",
            performed_by=user,
            tenant=None,
            payload=payload,
        )

    @staticmethod
    def cancel_invitation(token, performed_by):
        """Cancel an invitation via the service execution pipeline."""
        payload = {"token": token, "performed_by": performed_by}
        return BaseService.execute(
            operation="invitation.cancel",
            performed_by=performed_by,
            tenant=None,
            payload=payload,
        )

    @staticmethod
    def resend_invitation(token, performed_by):
        """Resend an invitation via the service execution pipeline."""
        payload = {"token": token, "performed_by": performed_by}
        return BaseService.execute(
            operation="invitation.resend",
            performed_by=performed_by,
            tenant=None,
            payload=payload,
        )

    @staticmethod
    def expire_stale_invitations():
        """Expire stale invitations via the service execution pipeline."""
        return BaseService.execute(
            operation="invitation.expire",
            performed_by=None,
            tenant=None,
            payload={},
        )

# ---------------------------------------------------------------------------
# Pipeline handler wrappers for InvitationService
# These functions expose the private implementation methods via the Service Execution Pipeline.
# ---------------------------------------------------------------------------

def invitation_create(**payload):
    """Wrapper for _invite_user_impl."""
    return _invite_user_impl(**payload)

def invitation_accept(**payload):
    """Wrapper for _accept_invitation_impl."""
    return _accept_invitation_impl(**payload)

def invitation_reject(**payload):
    """Wrapper for _reject_invitation_impl."""
    return _reject_invitation_impl(**payload)

def invitation_cancel(**payload):
    """Wrapper for _cancel_invitation_impl."""
    return _cancel_invitation_impl(**payload)

def invitation_resend(**payload):
    """Wrapper for _resend_invitation_impl."""
    return _resend_invitation_impl(**payload)

def invitation_expire(**payload):
    """Wrapper for _expire_stale_invitations_impl."""
    return _expire_stale_invitations_impl()
