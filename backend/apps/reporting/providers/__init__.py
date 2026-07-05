import abc
from typing import Any, Dict, List
from uuid import UUID

from ..dtos import ExportDTO, ReportDTO, SectionDTO, TemplateDTO


class BaseReportProvider(abc.ABC):
    """Handles assembly of reports from various contexts."""
    @abc.abstractmethod
    def assemble_report_payload(self, report: ReportDTO, template: TemplateDTO, sections: List[SectionDTO]) -> Dict[str, Any]:
        """Aggregates intelligence into a complete report payload according to the template."""
        pass


class BaseTemplateProvider(abc.ABC):
    """Handles rendering of report sections using templates."""
    @abc.abstractmethod
    def render_section(self, section: SectionDTO, context: Dict[str, Any]) -> str:
        """Renders a specific section based on its type and configuration."""
        pass


class BaseExportProvider(abc.ABC):
    """Handles generation of export artifacts (PDF, DOCX, etc)."""
    @abc.abstractmethod
    def generate_export(self, payload: Dict[str, Any], format: str) -> ExportDTO:
        """Transforms a rendered report payload into the desired format and returns artifact metadata."""
        pass


class InternalReportProvider(BaseReportProvider):
    """Internal implementation that coordinates with platform selectors."""
    def assemble_report_payload(self, report: ReportDTO, template: TemplateDTO, sections: List[SectionDTO]) -> Dict[str, Any]:
        # Implementation would call selectors from timeline, graph, evidence, etc.
        # to build out the payload.
        return {"assembled": True, "title": report.title, "sections": []}

__all__ = [
    "BaseReportProvider",
    "BaseTemplateProvider",
    "BaseExportProvider",
    "InternalReportProvider",
]
