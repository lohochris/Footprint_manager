from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db import transaction

from backend.shared.event_bus import event_bus

from ..dtos import SecurityContext
from ..models import SecurityEvent, SecurityPolicy
from ..repositories import EventRepository, PolicyRepository, SessionRepository


class SecurityEngine:
    """Coordinates policy evaluation, MFA workflows, session validation, and security events."""

    def __init__(
        self,
        policy_repository: PolicyRepository,
        session_repository: SessionRepository,
        event_repository: EventRepository,
    ):
        self.policy_repository = policy_repository
        self.session_repository = session_repository
        self.event_repository = event_repository

    def evaluate_context(self, context: SecurityContext) -> bool:
        """Evaluates whether the given context satisfies current security policies."""
        policy = self.policy_repository.get_active_policy(context.tenant_id)
        if not policy:
            return True  # No policy to enforce

        if policy.require_mfa and not context.is_mfa_authenticated:
            self._log_and_publish(
                SecurityEvent.EventType.FAILED_LOGIN,
                context,
                {"reason": "MFA required but not provided"},
            )
            return False

        if policy.allowed_ips and context.ip_address not in policy.allowed_ips:
            self._log_and_publish(
                SecurityEvent.EventType.FAILED_LOGIN,
                context,
                {"reason": f"IP {context.ip_address} not in allowed list"},
            )
            return False

        if context.session_id:
            session = self.session_repository.get_active_session(context.session_id)
            if not session:
                return False

            # Check session timeout
            delta = datetime.now() - session.last_activity.replace(tzinfo=None)
            if delta.total_seconds() / 60 > policy.session_timeout_minutes:
                session.is_active = False
                session.save(update_fields=["is_active"])
                self._log_and_publish(
                    SecurityEvent.EventType.SESSION_REVOKED,
                    context,
                    {"reason": "Session timeout"},
                )
                return False

        return True

    @transaction.atomic
    def _log_and_publish(self, event_type: str, context: SecurityContext, details: dict) -> None:
        """Logs the event locally and publishes to the domain event bus."""
        event = self.event_repository.log_event(
            event_type=event_type,
            tenant_id=context.tenant_id,
            organization_id=context.organization_id,
            actor_id=context.user_id,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            details=details,
        )

        event_bus.publish(
            "SecurityAlertGenerated" if event_type in [SecurityEvent.EventType.FAILED_LOGIN] else event_type,
            {
                "event_id": str(event.id),
                "event_type": event_type,
                "context": context.as_dict(),
                "details": details,
            },
        )

__all__ = ["SecurityEngine"]
