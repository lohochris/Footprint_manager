from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from ..models import (
    Report,
    ReportAudit,
    ReportExport,
    ReportSection,
    ReportTemplate,
    ReportVersion,
)


class ReportRepository:
    def create_report(
        self,
        title: str,
        report_type: str,
        tenant_id: UUID,
        organization_id: UUID,
        author_id: Optional[UUID] = None,
        investigation_id: Optional[UUID] = None,
        template_id: Optional[UUID] = None,
    ) -> Report:
        return Report.objects.create(
            title=title,
            report_type=report_type,
            workspace_id=tenant_id,
            organization_id=organization_id,
            author_id=author_id,
            investigation_id=investigation_id,
            template_id=template_id,
        )

    def get_report(self, report_id: UUID, tenant_id: UUID) -> Optional[Report]:
        try:
            return Report.objects.get(id=report_id, workspace_id=tenant_id)
        except ObjectDoesNotExist:
            return None


class TemplateRepository:
    def get_template(self, template_id: UUID, tenant_id: UUID) -> Optional[ReportTemplate]:
        try:
            return ReportTemplate.objects.get(id=template_id, workspace_id=tenant_id)
        except ObjectDoesNotExist:
            return None


class VersionRepository:
    def create_version(
        self,
        report: Report,
        version_number: int,
        status: str,
        payload: Dict[str, Any],
        tenant_id: UUID,
        organization_id: UUID,
        created_by_id: Optional[UUID] = None,
    ) -> ReportVersion:
        return ReportVersion.objects.create(
            report=report,
            version_number=version_number,
            status=status,
            payload=payload,
            workspace_id=tenant_id,
            organization_id=organization_id,
            created_by_id=created_by_id,
        )


class ExportRepository:
    def create_export(
        self,
        report_version: ReportVersion,
        export_format: str,
        file_url: str,
        tenant_id: UUID,
        organization_id: UUID,
        created_by_id: Optional[UUID] = None,
    ) -> ReportExport:
        return ReportExport.objects.create(
            report_version=report_version,
            export_format=export_format,
            file_url=file_url,
            workspace_id=tenant_id,
            organization_id=organization_id,
            created_by_id=created_by_id,
        )


class AuditRepository:
    def log_operation(
        self,
        operation_type: str,
        tenant_id: UUID,
        organization_id: UUID,
        report: Optional[Report] = None,
        actor_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> ReportAudit:
        return ReportAudit.objects.create(
            operation_type=operation_type,
            workspace_id=tenant_id,
            organization_id=organization_id,
            report=report,
            actor_id=actor_id,
            details=details or {},
            ip_address=ip_address,
        )

__all__ = [
    "ReportRepository",
    "TemplateRepository",
    "VersionRepository",
    "ExportRepository",
    "AuditRepository",
]
