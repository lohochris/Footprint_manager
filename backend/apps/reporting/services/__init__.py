from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.db import transaction

from backend.shared.event_bus import event_bus

from ..dtos import ExportDTO, ReportDTO, SectionDTO, TemplateDTO
from ..models import Report, ReportAudit, ReportExport, ReportVersion
from ..providers import BaseExportProvider, BaseReportProvider, BaseTemplateProvider
from ..repositories import (
    AuditRepository,
    ExportRepository,
    ReportRepository,
    VersionRepository,
)


class ReportService:
    def __init__(self, repository: ReportRepository, provider: BaseReportProvider):
        self.repository = repository
        self.provider = provider

    @transaction.atomic
    def draft_report(
        self,
        title: str,
        report_type: str,
        template_id: UUID,
        tenant_id: UUID,
        organization_id: UUID,
        author_id: UUID,
        investigation_id: Optional[UUID] = None,
    ) -> Report:
        report = self.repository.create_report(
            title=title,
            report_type=report_type,
            tenant_id=tenant_id,
            organization_id=organization_id,
            author_id=author_id,
            investigation_id=investigation_id,
            template_id=template_id,
        )
        return report

    def assemble_content(self, report_dto: ReportDTO, template_dto: TemplateDTO, sections: List[SectionDTO]) -> Dict[str, Any]:
        """Uses the provider to gather data from external selectors (Graph, Timeline, Evidence)"""
        return self.provider.assemble_report_payload(report_dto, template_dto, sections)


class PublishingService:
    def __init__(self, version_repository: VersionRepository, audit_repository: AuditRepository):
        self.version_repository = version_repository
        self.audit_repository = audit_repository

    @transaction.atomic
    def publish_report(
        self,
        report: Report,
        payload: Dict[str, Any],
        tenant_id: UUID,
        organization_id: UUID,
        actor_id: UUID,
    ) -> ReportVersion:
        
        # Any modification or publishing creates a new immutable version
        new_version_number = report.version + 1
        
        version = self.version_repository.create_version(
            report=report,
            version_number=new_version_number,
            status=Report.Status.PUBLISHED,
            payload=payload,
            tenant_id=tenant_id,
            organization_id=organization_id,
            created_by_id=actor_id,
        )

        report.status = Report.Status.PUBLISHED
        report.version = new_version_number
        report.published_at = datetime.now()
        report.save(update_fields=["status", "version", "published_at"])

        self.audit_repository.log_operation(
            operation_type=ReportAudit.OperationType.PUBLICATION,
            tenant_id=tenant_id,
            organization_id=organization_id,
            report=report,
            actor_id=actor_id,
            details={"version": new_version_number},
        )

        event_bus.publish(
            "ReportPublished",
            {
                "report_id": str(report.id),
                "version": new_version_number,
                "tenant_id": str(tenant_id),
                "organization_id": str(organization_id),
                "actor_id": str(actor_id),
            },
        )

        return version


class TemplateService:
    def __init__(self, provider: BaseTemplateProvider):
        self.provider = provider

    def render(self, section: SectionDTO, context: Dict[str, Any]) -> str:
        """Renders the section structure with actual data context."""
        return self.provider.render_section(section, context)


class ExportService:
    def __init__(
        self,
        export_repository: ExportRepository,
        audit_repository: AuditRepository,
        provider: BaseExportProvider,
    ):
        self.export_repository = export_repository
        self.audit_repository = audit_repository
        self.provider = provider

    @transaction.atomic
    def export_report_version(
        self,
        report_version: ReportVersion,
        format: str,
        tenant_id: UUID,
        organization_id: UUID,
        actor_id: UUID,
    ) -> ReportExport:
        
        # Provider handles the actual generation (e.g. converting HTML payload to PDF)
        export_dto = self.provider.generate_export(report_version.payload, format)
        
        export = self.export_repository.create_export(
            report_version=report_version,
            export_format=format,
            file_url=export_dto.file_url,
            tenant_id=tenant_id,
            organization_id=organization_id,
            created_by_id=actor_id,
        )

        self.audit_repository.log_operation(
            operation_type=ReportAudit.OperationType.EXPORT,
            tenant_id=tenant_id,
            organization_id=organization_id,
            report=report_version.report,
            actor_id=actor_id,
            details={"format": format, "version": report_version.version_number},
        )

        event_bus.publish(
            "ReportExported",
            {
                "report_id": str(report_version.report.id),
                "version": report_version.version_number,
                "format": format,
                "tenant_id": str(tenant_id),
                "organization_id": str(organization_id),
                "actor_id": str(actor_id),
            },
        )

        return export

__all__ = [
    "ReportService",
    "PublishingService",
    "TemplateService",
    "ExportService",
]
