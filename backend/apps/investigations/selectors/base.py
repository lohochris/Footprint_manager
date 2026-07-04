# backend/apps/investigations/selectors/base.py
"""Base selector providing common read‑only query functionality for the investigations app.

Selectors are thin layers that expose filtered, searchable, ordered, and paginated
querysets without mutating data. All concrete selectors inherit from this class
and set the ``model`` attribute to the appropriate Django model.
"""

from typing import Any

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Model, QuerySet


class BaseSelector:
    """Common selector functionality for read‑only queries.

    Sub‑classes must define a ``model`` attribute pointing to a Django model
    class. The ``tenant_field`` defaults to ``tenant_id`` which matches the
    foreign key used for tenant isolation throughout the project.
    """

    model: type[Model]
    tenant_field = "tenant_id"

    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id

    def _base_qs(self) -> QuerySet:
        """Base queryset filtered by tenant.
        """
        return self.model.objects.filter(**{self.tenant_field: self.tenant_id})  # type: ignore[attr-defined]

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        ordering: list[str] | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Return a paginated, filtered, ordered, searchable result set.

        * ``filters`` – exact match dict passed to ``queryset.filter``.
        * ``ordering`` – list of field names (``-field`` for descending).
        * ``search`` – case‑insensitive search across ``search_fields`` defined
          on the concrete selector.
        * ``page``/``page_size`` – standard DRF‑style pagination.
        """
        qs = self._base_qs()

        if filters:
            qs = qs.filter(**filters)

        if search:
            search_fields = getattr(self, "search_fields", [])
            if search_fields:
                from django.db.models import Q

                query = Q()
                for field in search_fields:
                    query |= Q(**{f"{field}__icontains": search})
                qs = qs.filter(query)

        if ordering:
            qs = qs.order_by(*ordering)

        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)

        return {
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "results": list(page_obj.object_list),
            "page": page_obj.number,
            "page_size": page_size,
        }
