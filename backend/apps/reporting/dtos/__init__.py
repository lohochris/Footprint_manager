from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class ReportDTO:
    id: UUID
    title: str
    report_type: str
    status: str
    author_id: Optional[UUID]
    investigation_id: Optional[UUID]
    template_id: Optional[UUID]
    version: int
    published_at: Optional[datetime]


@dataclass
class TemplateDTO:
    id: UUID
    name: str
    description: str
    template_type: str
    is_active: bool
    version: int


@dataclass
class SectionDTO:
    id: UUID
    template_id: UUID
    title: str
    section_type: str
    order: int
    configuration: Dict[str, Any]


@dataclass
class VersionDTO:
    id: UUID
    report_id: UUID
    version_number: int
    status: str
    payload: Dict[str, Any]
    created_at: datetime
    created_by_id: Optional[UUID]


@dataclass
class ExportDTO:
    id: UUID
    report_version_id: UUID
    export_format: str
    file_url: str
    created_at: datetime
    created_by_id: Optional[UUID]


@dataclass
class AuditDTO:
    id: UUID
    operation_type: str
    report_id: Optional[UUID]
    actor_id: Optional[UUID]
    timestamp: datetime
    details: Dict[str, Any]
    ip_address: Optional[str]
