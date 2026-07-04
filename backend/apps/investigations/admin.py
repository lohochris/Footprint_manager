from django.contrib import admin

from .models import (
    EvidenceReference,
    Investigation,
    InvestigationComment,
    InvestigationMember,
    InvestigationTarget,
    InvestigationTimelineEvent,
)


@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    list_display = (
        "case_number",
        "title",
        "organization",
        "workspace",
        "status",
        "priority",
        "investigation_type",
        "created_at",
    )
    list_filter = ("status", "priority", "investigation_type", "is_archived", "is_deleted")
    search_fields = ("case_number", "title", "description")
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "deleted_at",
        "archived_at",
    )


@admin.register(InvestigationMember)
class InvestigationMemberAdmin(admin.ModelAdmin):
    list_display = ("investigation", "user", "role", "permission_level", "active", "assigned_date")
    list_filter = ("role", "permission_level", "active")
    search_fields = ("investigation__case_number", "user__username", "user__email")
    readonly_fields = ("created_by", "updated_by", "assigned_date")


@admin.register(InvestigationTarget)
class InvestigationTargetAdmin(admin.ModelAdmin):
    list_display = ("display_name", "target_type", "investigation", "confidence", "source")
    list_filter = ("target_type", "confidence")
    search_fields = ("display_name", "investigation__case_number", "source")
    readonly_fields = ("created_by", "updated_by")


@admin.register(EvidenceReference)
class EvidenceReferenceAdmin(admin.ModelAdmin):
    list_display = ("reference_type", "source", "external_identifier", "investigation", "linked_by", "linked_at")
    list_filter = ("reference_type", "source")
    search_fields = ("source", "external_identifier", "uri", "hash_value", "summary", "investigation__case_number")
    readonly_fields = ("created_by", "updated_by", "linked_at")


@admin.register(InvestigationTimelineEvent)
class InvestigationTimelineEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "investigation", "timestamp", "description")
    list_filter = ("event_type", "timestamp")
    search_fields = ("description", "investigation__case_number")

    # Timeline events are immutable, so all fields are readonly in admin
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(InvestigationComment)
class InvestigationCommentAdmin(admin.ModelAdmin):
    list_display = ("investigation", "author", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("rich_content", "investigation__case_number", "author__username")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by", "deleted_at")
