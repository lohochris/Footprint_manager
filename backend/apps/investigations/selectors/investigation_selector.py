"""Selector layer for Investigation domain.
Provides read‑only queryset helpers scoped to the tenant (organization).
"""

from typing import Any

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from backend.apps.organizations.models import Organization

from ..models import investigation as inv_models


class InvestigationSelector:
    """Read‑only queries for Investigation objects.

    All methods return QuerySets or serializable data structures; no side‑effects.
    """

    @staticmethod
    def base_queryset(tenant: Organization):
        """Base queryset scoped to the given tenant (organization)."""
        return inv_models.Investigation.objects.filter(
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
    ) -> tuple[list[inv_models.Investigation], dict[str, Any]]:
        """Return paginated list of investigations with optional filtering/search.
        Returns a tuple of (items, pagination_meta).
        """
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
    def retrieve(tenant: Organization, pk: str) -> inv_models.Investigation:
        """Retrieve a single Investigation by primary key, scoped to tenant."""
        return InvestigationSelector.base_queryset(tenant).get(pk=pk)
