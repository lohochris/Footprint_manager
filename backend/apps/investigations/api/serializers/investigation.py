from django.core.exceptions import ValidationError
from rest_framework import serializers

from backend.apps.investigations.models import Investigation
from backend.apps.investigations.validators.investigation_validator import (
    validate_priority,
    validate_tags,
)

from .member import InvestigationMemberSerializer
from .target import InvestigationTargetSerializer
from .evidence import EvidenceReferenceSerializer
from .comment import InvestigationCommentSerializer
from .timeline import InvestigationTimelineEventSerializer


class InvestigationSerializer(serializers.ModelSerializer):
    """General serializer for the Investigation model."""

    owner_username = serializers.CharField(source="owner.username", read_only=True)
    lead_investigator_username = serializers.CharField(source="lead_investigator.username", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)

    class Meta:
        model = Investigation
        fields = (
            "id",
            "case_number",
            "title",
            "description",
            "organization",
            "organization_name",
            "workspace",
            "workspace_name",
            "owner",
            "owner_username",
            "lead_investigator",
            "lead_investigator_username",
            "investigation_type",
            "status",
            "priority",
            "classification",
            "tags",
            "metadata",
            "is_archived",
            "archived_at",
            "closed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "case_number",
            "organization",
            "owner",
            "is_archived",
            "archived_at",
            "closed_at",
            "created_at",
            "updated_at",
        )


class InvestigationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new Investigation."""

    class Meta:
        model = Investigation
        fields = (
            "title",
            "description",
            "workspace",
            "investigation_type",
            "priority",
            "classification",
            "tags",
            "metadata",
        )
        extra_kwargs = {
            "title": {"required": True},
            "workspace": {"required": False, "allow_null": True},
            "investigation_type": {"required": False},
            "priority": {"required": False},
            "classification": {"required": False},
            "tags": {"required": False},
            "metadata": {"required": False},
        }

    def validate_priority(self, value):
        try:
            validate_priority(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate_tags(self, value):
        try:
            validate_tags(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value


class InvestigationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating mutable fields of an Investigation."""

    class Meta:
        model = Investigation
        fields = (
            "title",
            "description",
            "priority",
            "classification",
            "tags",
            "metadata",
        )
        extra_kwargs = {
            "title": {"required": False},
            "description": {"required": False},
            "priority": {"required": False},
            "classification": {"required": False},
            "tags": {"required": False},
            "metadata": {"required": False},
        }

    def validate_priority(self, value):
        try:
            validate_priority(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate_tags(self, value):
        try:
            validate_tags(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value


class InvestigationDetailSerializer(serializers.ModelSerializer):
    """Read-only representation of an Investigation with all related sub-entities."""

    owner_username = serializers.CharField(source="owner.username", read_only=True)
    lead_investigator_username = serializers.CharField(source="lead_investigator.username", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)

    members = InvestigationMemberSerializer(many=True, read_only=True)
    targets = InvestigationTargetSerializer(many=True, read_only=True)
    evidence_references = EvidenceReferenceSerializer(many=True, read_only=True)
    comments = InvestigationCommentSerializer(many=True, read_only=True)
    timeline_events = InvestigationTimelineEventSerializer(many=True, read_only=True)

    class Meta:
        model = Investigation
        fields = (
            "id",
            "case_number",
            "title",
            "description",
            "organization",
            "organization_name",
            "workspace",
            "workspace_name",
            "owner",
            "owner_username",
            "lead_investigator",
            "lead_investigator_username",
            "investigation_type",
            "status",
            "priority",
            "classification",
            "tags",
            "metadata",
            "is_archived",
            "archived_at",
            "closed_at",
            "created_at",
            "updated_at",
            "members",
            "targets",
            "evidence_references",
            "comments",
            "timeline_events",
        )
        read_only_fields = fields
