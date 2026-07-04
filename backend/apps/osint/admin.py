# backend/apps/osint/admin.py
"""Django Admin registrations for the OSINT Discovery domain.

All three aggregate roots are registered with useful ``list_display``,
``list_filter``, ``search_fields``, and ``readonly_fields`` so that the
admin provides immediate operational visibility without requiring custom
views.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import DiscoveryJob, DiscoveryProvider, DiscoveryResult


@admin.register(DiscoveryProvider)
class DiscoveryProviderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_name",
        "version",
        "provider_status",
        "priority",
        "timeout_seconds",
        "max_retries",
        "is_active",
        "last_health_status",
        "last_health_check_at",
    )
    list_filter = ("provider_status", "is_active", "last_health_status")
    search_fields = ("name", "display_name", "description")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "last_health_check_at",
        "last_health_status",
        "last_health_message",
    )
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "id",
                    "name",
                    "display_name",
                    "version",
                    "description",
                )
            },
        ),
        (
            "Status & Routing",
            {
                "fields": (
                    "provider_status",
                    "is_active",
                    "priority",
                    "timeout_seconds",
                    "max_retries",
                )
            },
        ),
        (
            "Capabilities",
            {"fields": ("capabilities",)},
        ),
        (
            "Health Snapshot",
            {
                "fields": (
                    "last_health_check_at",
                    "last_health_status",
                    "last_health_message",
                )
            },
        ),
        (
            "Configuration",
            {
                "classes": ("collapse",),
                "fields": ("configuration",),
                "description": "Provider credentials. Treat as sensitive data.",
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
            },
        ),
    )
    ordering = ("priority", "name")


@admin.register(DiscoveryJob)
class DiscoveryJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "provider_name",
        "status",
        "triggered_by",
        "started_at",
        "completed_at",
        "duration_ms",
        "retry_count",
        "created_at",
    )
    list_filter = ("status", "triggered_by", "provider")
    search_fields = ("id", "provider__name", "failure_reason")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
        "duration_ms",
        "retry_count",
    )
    raw_id_fields = ("provider", "investigation", "target")
    fieldsets = (
        (
            "Identity",
            {"fields": ("id", "status", "triggered_by")},
        ),
        (
            "Assignment",
            {"fields": ("provider", "investigation", "target")},
        ),
        (
            "Execution Input",
            {"fields": ("capabilities_requested", "input_data")},
        ),
        (
            "Execution Metadata",
            {
                "fields": (
                    "started_at",
                    "completed_at",
                    "duration_ms",
                    "failure_reason",
                    "retry_count",
                    "scheduled_at",
                )
            },
        ),
        (
            "Supplementary",
            {
                "classes": ("collapse",),
                "fields": ("metadata",),
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
            },
        ),
    )
    ordering = ("-created_at",)

    @admin.display(description="Provider")
    def provider_name(self, obj: DiscoveryJob) -> str:
        return obj.provider.name if obj.provider_id else "—"


@admin.register(DiscoveryResult)
class DiscoveryResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "result_type",
        "title",
        "confidence_display",
        "is_verified",
        "job_id",
        "provider_name",
        "created_at",
    )
    list_filter = ("result_type", "is_verified", "provider")
    search_fields = ("title", "summary", "source_url", "tags")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("job", "provider")
    fieldsets = (
        (
            "Classification",
            {"fields": ("job", "provider", "result_type", "title", "summary")},
        ),
        (
            "Confidence",
            {"fields": ("confidence", "is_verified", "verified_by_id")},
        ),
        (
            "Payload",
            {"fields": ("raw_data", "normalised_data")},
        ),
        (
            "Provenance",
            {
                "fields": (
                    "storage_key",
                    "evidence_id",
                    "source_url",
                    "tags",
                )
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": ("id", "created_at", "updated_at", "created_by", "updated_by"),
            },
        ),
    )
    ordering = ("-confidence", "-created_at")

    @admin.display(description="Confidence", ordering="confidence")
    def confidence_display(self, obj: DiscoveryResult) -> str:
        pct = float(obj.confidence) * 100
        return format_html("<strong>{:.1f}%</strong>", pct)

    @admin.display(description="Provider")
    def provider_name(self, obj: DiscoveryResult) -> str:
        return obj.provider.name if obj.provider is not None else "—"
