import logging
from typing import Any

from apps.audit.models import AuditLog
from apps.common.pipeline.core import ExecutionResult, Pipeline, PipelineContext, PipelineStage
from apps.common.pipeline.registry import PipelineRegistry
from django.core.exceptions import PermissionDenied
from django.utils import timezone

logger = logging.getLogger(__name__)


class BaseService:
    """Common infrastructure for all domain services.

    Provides:
    * Tenant isolation helpers
    * Permission checking utilities
    * Audit‑log creation
    * Domain‑event publishing (stubbed)
    * Generic transaction wrapper (via @transaction.atomic on concrete methods)
    """

    @staticmethod
    def get_tenant(user):
        """Return the tenant (organization) associated with the user.
        Assumes a ``tenant`` attribute or ``organization`` foreign key on the user model.
        """
        return getattr(user, "tenant", getattr(user, "organization", None))

    @staticmethod
    def enforce_tenant_scope(instance, user):
        """Ensure the instance belongs to the same tenant as the user.
        Raises ``PermissionDenied`` if the tenant does not match.
        """
        tenant = BaseService.get_tenant(user)
        if hasattr(instance, "tenant") and instance.tenant != tenant:
            raise PermissionDenied("Object does not belong to the user's tenant.")
        if hasattr(instance, "organization") and instance.organization != tenant:
            raise PermissionDenied("Object does not belong to the user's organization.")

    @staticmethod
    def check_permission(user, action, obj=None):
        """Placeholder permission check.
        In a real system this would delegate to a RBAC engine.
        Here we simply log and assume the user has permission.
        """
        logger.debug("Permission check: user=%s action=%s obj=%s", user, action, obj)
        # TODO: integrate with actual permission backend
        return True

    @staticmethod
    def log_audit(user, action, instance, details=None):
        """Create an audit‑log entry for a mutating operation."""
        AuditLog.objects.create(
            user=user,
            action=action,
            object_id=instance.pk,
            object_repr=str(instance),
            details=details or {},
            timestamp=timezone.now(),
        )

    @staticmethod
    def publish_event(event_name, payload):
        """Stub for domain‑event publishing.
        Replace with actual event bus (e.g., Django signals, Celery, etc.).
        """
        logger.info("Domain event published: %s payload=%s", event_name, payload)
        # No‑op implementation – extend as needed.

    @staticmethod
    def execute(operation: str, performed_by: Any, tenant: Any, payload: dict[str, Any], metadata: dict[str, Any] | None = None) -> ExecutionResult:
        """Facade to execute a service operation via the pipeline.

        Args:
            operation: Dotted operation name, e.g., "organization.create".
            performed_by: The user or service invoking the operation.
            tenant: Tenant identifier (organization).
            payload: Input data for the handler.
            metadata: Additional context metadata.
        """
        if metadata is None:
            metadata = {}
        # Resolve handler from registry
        handler = PipelineRegistry.get_handler(operation)
        # Initialize pipeline context
        context = PipelineContext(
            performed_by=performed_by,
            tenant=tenant,
            payload=payload,
            metadata=metadata,
        )
        # Simple stage that invokes the handler
        class _HandlerStage(PipelineStage):
            priority = 1000
            name = "BusinessLogicStage"

            def execute(self, ctx: PipelineContext) -> PipelineContext:
                # Handler may accept **payload if dict, else a single argument
                if isinstance(ctx.payload, dict):
                    result = handler(**ctx.payload)
                else:
                    result = handler(ctx.payload)
                return ctx.with_updates(payload=result)

        pipeline = Pipeline([_HandlerStage()])
        return pipeline.run(context)
