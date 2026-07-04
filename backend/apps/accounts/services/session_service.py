from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.utils import timezone

from ..models.account_activity import AccountActivity
from ..models.session import Session


class SessionService:
    """Service handling user session management.

    Provides listing of active sessions, revocation of a specific session, and
    revocation of all sessions except the current one. All mutating operations
    are performed inside a transaction to guarantee consistency.
    """

    @staticmethod
    def list_user_sessions(user) -> list[Session]:
        """Return all sessions belonging to *user* that are not logged out.

        Args:
            user: Django ``User`` instance.
        Returns:
            List of ``Session`` objects with status ``ACTIVE``.
        """
        return list(Session.objects.filter(user=user, status=Session.Status.ACTIVE))

    @staticmethod
    def _validate_ownership(user, session: Session) -> None:
        """Ensure the session belongs to the user.

        Raises ``PermissionDenied`` if the session is owned by another user.
        """
        if session.user_id != user.id:
            raise PermissionDenied("You do not have permission to manage this session.")

    @staticmethod
    def _log_activity(user, action: str, session: Session, request=None) -> None:
        """Create an ``AccountActivity`` entry for a session‑related action.

        ``request`` is optional; if provided, its IP, user‑agent and ID are
        captured. This keeps audit information consistent across the
        application.
        """
        metadata = {
            "session_id": str(session.id),
            "ip_address": getattr(request, "META", {}).get("REMOTE_ADDR", "") if request else "",
            "user_agent": getattr(request, "META", {}).get("HTTP_USER_AGENT", "") if request else "",
        }
        AccountActivity.objects.create(
            user=user,
            action=action,
            ip_address=metadata["ip_address"],
            user_agent=metadata["user_agent"],
            request_id=getattr(request, "request_id", "") if request else "",
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def revoke_session(user, session_id: UUID, request=None) -> None:
        """Revoke a single session identified by ``session_id``.

        The target session must belong to ``user`` and be active. The session
        status is set to ``LOGGED_OUT`` and ``logout_time`` is recorded.
        """
        try:
            session = Session.objects.select_for_update().get(id=str(session_id))
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Session {session_id} not found.")

        SessionService._validate_ownership(user, session)

        if session.status != Session.Status.ACTIVE:
            raise PermissionDenied("Session is not active and cannot be revoked.")

        session.status = Session.Status.LOGGED_OUT
        session.logout_time = timezone.now()
        session.save(update_fields=["status", "logout_time"])

        SessionService._log_activity(user, "SESSION_REVOKED", session, request)

    @staticmethod
    @transaction.atomic
    def revoke_other_sessions(user, current_session_id: UUID, request=None) -> None:
        """Revoke all active sessions for *user* except ``current_session_id``.

        The current session is left untouched. Each revoked session is logged.
        """
        active_sessions = Session.objects.select_for_update().filter(
            user=user,
            status=Session.Status.ACTIVE,
        ).exclude(id=str(current_session_id))

        now = timezone.now()
        for session in active_sessions:
            session.status = Session.Status.LOGGED_OUT
            session.logout_time = now
            session.save(update_fields=["status", "logout_time"])
            SessionService._log_activity(user, "ALL_SESSIONS_REVOKED", session, request)
