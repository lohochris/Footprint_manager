# Workspace serializers for the organizations app

"""Serializers handling Workspace model CRUD operations.

The original project expected these serializers in a module
`backend.apps.organizations.serializers.workspace`, but the file was missing,
causing an import error during test discovery. This implementation provides
minimal, functional serializers that map directly to the `Workspace` model and
expose the fields required by the viewset.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models.organization import Organization
from ..models.workspace import Workspace

User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    """Read‑only representation of a Workspace.

    All model fields are included; read‑only fields are handled by the viewset
    logic.
    """

    class Meta:
        model = Workspace
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkspaceCreateSerializer(serializers.Serializer):
    """Serializer for creating a Workspace.

    It validates the required fields and returns the validated data for the
    service layer to handle the actual creation.
    """

    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=150)
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    # Owner will be taken from the request user in the viewset.

    def validate_slug(self, value):
        # Placeholder for uniqueness validation; the service layer performs the
        # definitive check.
        return value

    def create(self, validated_data):
        # The viewset delegates creation to the WorkspaceService, so we simply
        # return the validated data.
        return validated_data


class WorkspaceUpdateSerializer(serializers.Serializer):
    """Serializer for updating mutable Workspace fields.

    Currently only ``name`` and ``description`` are updatable; extra fields can
    be added as the model evolves.
    """

    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    # Additional mutable fields can be added here.

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WorkspaceSettingsSerializer(serializers.Serializer):
    """Serializer for the JSON ``settings`` field of a Workspace.

    The service layer validates the schema; this serializer simply passes the
    JSON payload through.
    """

    settings = serializers.JSONField()

    def update(self, instance, validated_data):
        instance.settings = validated_data["settings"]
        instance.save()
        return instance
