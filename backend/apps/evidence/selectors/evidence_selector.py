from typing import Any
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from backend.apps.organizations.models import Organization
from backend.apps.evidence.models import Evidence, EvidenceCustodyEvent


class EvidenceSelector:
    """Read-only queries for Evidence aggregate and related sub-entities."""

    @staticmethod
    def base_queryset(tenant: Organization):
        """Base queryset scoped to the given tenant (organization)."""
        return Evidence.objects.filter(
            tenant_id=tenant.id,
            is_deleted=False,
        )

    @staticmethod
    def list(
        tenant: Organization,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Evidence], dict[str, Any]]:
        """Return paginated list of evidence items with optional filtering/search."""
        qs = EvidenceSelector.base_queryset(tenant)

        if filters:
            if status := filters.get("status"):
                qs = qs.filter(status=status)
            if classification := filters.get("classification"):
                qs = qs.filter(classification=classification)
            if current_custodian_id := filters.get("current_custodian_id"):
                qs = qs.filter(current_custodian_id=current_custodian_id)
            if workspace_id := filters.get("workspace_id"):
                qs = qs.filter(workspace_id=workspace_id)

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        if ordering:
            qs = qs.order_by(*ordering)
        else:
            qs = qs.order_by("-created_at")

        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)

        meta = {
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }
        return list(page_obj.object_list), meta

    @staticmethod
    def retrieve(tenant: Organization, pk: str) -> Evidence:
        """Retrieve a single Evidence aggregate by primary key, scoped to tenant."""
        return EvidenceSelector.base_queryset(tenant).get(pk=pk)

    @staticmethod
    def get_custody_history(evidence: Evidence):
        """Return QuerySet of custody events for the evidence item."""
        return EvidenceCustodyEvent.objects.filter(
            evidence=evidence,
            is_deleted=False,
        ).order_by("-taken_at")
