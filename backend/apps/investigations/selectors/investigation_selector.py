from typing import Any
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from backend.apps.organizations.models import Organization
from ..models import (
    Investigation,
    InvestigationMember,
    InvestigationTarget,
    InvestigationTimelineEvent,
    InvestigationComment,
)


class InvestigationSelector:
    """Read‑only queries for Investigation objects and related sub-entities."""

    @staticmethod
    def base_queryset(tenant: Organization):
        """Base queryset scoped to the given tenant (organization)."""
        return Investigation.objects.filter(
            organization=tenant,
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
    ) -> tuple[list[Investigation], dict[str, Any]]:
        """Return paginated list of investigations with optional filtering/search."""
        qs = InvestigationSelector.base_queryset(tenant)

        if filters:
            if status := filters.get("status"):
                qs = qs.filter(status__in=status)
            if priority := filters.get("priority"):
                qs = qs.filter(priority__in=priority)
            if visibility := filters.get("visibility"):
                qs = qs.filter(visibility__in=visibility)
            if tags := filters.get("tags"):
                for tag in tags:
                    qs = qs.filter(tags__contains=[tag])
            if owner_id := filters.get("owner_id"):
                qs = qs.filter(owner_id=owner_id)

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(case_number__icontains=search)
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
    def retrieve(tenant: Organization, pk: str) -> Investigation:
        """Retrieve a single Investigation by primary key, scoped to tenant."""
        return InvestigationSelector.base_queryset(tenant).get(pk=pk)

    @staticmethod
    def get_members(investigation: Investigation):
        """Return QuerySet of active members assigned to an investigation."""
        return InvestigationMember.objects.filter(investigation=investigation, active=True)

    @staticmethod
    def get_targets(investigation: Investigation):
        """Return QuerySet of target entities under observation."""
        return InvestigationTarget.objects.filter(investigation=investigation)

    @staticmethod
    def get_timeline(investigation: Investigation):
        """Return QuerySet of timeline events ordered by timestamp."""
        return InvestigationTimelineEvent.objects.filter(investigation=investigation).order_by("timestamp")

    @staticmethod
    def get_comments(investigation: Investigation):
        """Return QuerySet of active (non-deleted) comments."""
        return InvestigationComment.objects.filter(investigation=investigation, is_deleted=False)
