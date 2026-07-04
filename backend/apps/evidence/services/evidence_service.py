from typing import Any

from backend.apps.common.pipeline.core import BaseService, ExecutionResult
from backend.apps.evidence.models import Evidence


class EvidenceService:
    """Domain service interface for the Evidence Management context."""

    @staticmethod
    def upload_evidence(
        user: Any,
        organization: Any,
        workspace_id: Any,
        title: str,
        description: str,
        classification: str,
        file_obj: Any,
        investigation_id: Any = None,
    ) -> Evidence:
        """Uploads a new digital evidence asset via the pipeline."""
        payload = {
            "workspace_id": workspace_id,
            "title": title,
            "description": description,
            "classification": classification,
            "file": file_obj,
        }
        metadata = {}
        if investigation_id:
            metadata["investigation_id"] = investigation_id

        result: ExecutionResult = BaseService.execute(
            operation="evidence.upload",
            performed_by=user,
            tenant=organization,
            payload=payload,
            metadata=metadata,
        )

        if not result.success:
            raise result.error

        return result.data

    @staticmethod
    def transfer_custody(
        user: Any,
        organization: Any,
        evidence: Evidence,
        new_custodian: Any,
        notes: str = "",
    ) -> Evidence:
        """Transfers custody of an evidence item to another user."""
        payload = {
            "evidence": evidence,
            "new_custodian": new_custodian,
            "notes": notes,
        }
        metadata = {"new_custodian": new_custodian}

        result: ExecutionResult = BaseService.execute(
            operation="evidence.transfer_custody",
            performed_by=user,
            tenant=organization,
            payload=payload,
            metadata=metadata,
        )

        if not result.success:
            raise result.error

        return result.data

    @staticmethod
    def verify_integrity(
        user: Any,
        organization: Any,
        evidence: Evidence,
    ) -> Evidence:
        """Performs a checksum verification check against the stored file."""
        payload = {
            "evidence": evidence,
        }

        result: ExecutionResult = BaseService.execute(
            operation="evidence.verify_integrity",
            performed_by=user,
            tenant=organization,
            payload=payload,
        )

        if not result.success:
            raise result.error

        return result.data
