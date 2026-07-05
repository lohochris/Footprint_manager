from typing import List, Optional
from uuid import UUID

from django.db.models import QuerySet

from ..models import Report, ReportExport, ReportTemplate, ReportVersion


class ReportSelector:
    def get_investigation_reports(self, investigation_id: UUID, tenant_id: UUID) -> QuerySet[Report]:
        return Report.objects.filter(investigation_id=investigation_id, workspace_id=tenant_id).order_by("-created_at")

    def get_published_reports(self, tenant_id: UUID) -> QuerySet[Report]:
        return Report.objects.filter(status=Report.Status.PUBLISHED, workspace_id=tenant_id).order_by("-published_at")


class TemplateSelector:
    def get_active_templates(self, tenant_id: UUID) -> QuerySet[ReportTemplate]:
        return ReportTemplate.objects.filter(is_active=True, workspace_id=tenant_id).order_by("name")

    def get_template_by_type(self, template_type: str, tenant_id: UUID) -> Optional[ReportTemplate]:
        return ReportTemplate.objects.filter(
            template_type=template_type, is_active=True, workspace_id=tenant_id
        ).order_by("-version").first()


class ExportSelector:
    def get_exports_for_version(self, version_id: UUID, tenant_id: UUID) -> QuerySet[ReportExport]:
        return ReportExport.objects.filter(report_version_id=version_id, workspace_id=tenant_id).order_by("-created_at")


__all__ = [
    "ReportSelector",
    "TemplateSelector",
    "ExportSelector",
]
