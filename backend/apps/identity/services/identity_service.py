from typing import Any
from backend.apps.common.pipeline.core import BaseService, ExecutionResult
from backend.apps.identity.models import Identity


class IdentityService:
    """Domain service interface for the Identity Resolution and Entity Correlation context."""

    @staticmethod
    def resolve_identity(
        user: Any,
        tenant: Any,
        label: str,
        entity_type: str,
        source: str = "manual",
        workspace_id: Any = None,
        attributes: list[dict[str, Any]] | None = None,
    ) -> Identity:
        """Runs the identity resolution pipeline to match/de-duplicate and register a new identity."""
        payload = {
            "label": label,
            "entity_type": entity_type,
            "source": source,
            "workspace_id": workspace_id,
            "attributes": attributes or [],
        }

        result: ExecutionResult = BaseService.execute(
            operation="identity.resolve",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )

        if not result.success:
            raise result.error

        # Retrieve the resolved/created identity
        identity_id = result.data.get("identity_id")
        return Identity.objects.get(id=identity_id)

    @staticmethod
    def merge_identities(
        user: Any,
        tenant: Any,
        identity_a_id: Any,
        identity_b_id: Any,
    ) -> Identity:
        """Executes the merge pipeline to combine two duplicate identities inside an atomic transaction."""
        payload = {
            "identity_a_id": identity_a_id,
            "identity_b_id": identity_b_id,
        }

        result: ExecutionResult = BaseService.execute(
            operation="identity.merge",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )

        if not result.success:
            raise result.error

        return result.data

    @staticmethod
    def split_identity(
        user: Any,
        tenant: Any,
        merge_history_id: Any,
    ) -> Identity:
        """Reverts a merge action by splitting the combined identity back to its original constituents."""
        payload = {
            "merge_history_id": merge_history_id,
        }

        result: ExecutionResult = BaseService.execute(
            operation="identity.split",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )

        if not result.success:
            raise result.error

        return result.data
