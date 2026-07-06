import django_filters
from backend.apps.investigations.models import Investigation


class InvestigationFilter(django_filters.FilterSet):
    """Filter set for the Investigation model."""

    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    priority = django_filters.CharFilter(field_name="priority", lookup_expr="exact")
    investigation_type = django_filters.CharFilter(field_name="investigation_type", lookup_expr="exact")
    classification = django_filters.CharFilter(field_name="classification", lookup_expr="exact")
    organization = django_filters.UUIDFilter(field_name="organization_id", lookup_expr="exact")
    workspace = django_filters.CharFilter(method="filter_workspace")
    owner = django_filters.NumberFilter(field_name="owner_id", lookup_expr="exact")
    lead_investigator = django_filters.NumberFilter(field_name="lead_investigator_id", lookup_expr="exact")
    created_at = django_filters.DateTimeFromToRangeFilter(field_name="created_at")
    updated_at = django_filters.DateTimeFromToRangeFilter(field_name="updated_at")
    tags = django_filters.CharFilter(method="filter_tags")

    class Meta:
        model = Investigation
        fields = [
            "status",
            "priority",
            "investigation_type",
            "classification",
            "organization",
            "workspace",
            "owner",
            "lead_investigator",
            "created_at",
            "updated_at",
            "tags",
        ]

    def filter_tags(self, queryset, name, value):
        """Filter by a tag contained within the JSON list of tags."""
        if not value:
            return queryset
        return queryset.filter(tags__contains=[value])

    def filter_workspace(self, queryset, name, value):
        """Filter by workspace ID (UUID) or workspace slug."""
        if not value:
            return queryset
        import uuid
        try:
            uuid_val = uuid.UUID(value)
            return queryset.filter(workspace_id=uuid_val)
        except ValueError:
            return queryset.filter(workspace__slug=value)
