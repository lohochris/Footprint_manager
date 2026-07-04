from django.contrib.auth import get_user_model
from rest_framework import serializers

from backend.apps.evidence.models import (
    Evidence,
    EvidenceFile,
    EvidenceVersion,
    EvidenceCustodyEvent,
)

User = get_user_model()


class EvidenceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceFile
        fields = (
            "id",
            "checksum_sha256",
            "original_filename",
            "mime_type",
            "file_size",
            "uploaded_at",
        )


class EvidenceVersionSerializer(serializers.ModelSerializer):
    file_meta = EvidenceFileSerializer(source="file", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = EvidenceVersion
        fields = (
            "id",
            "version_number",
            "notes",
            "file_meta",
            "created_by_username",
            "created_at",
        )


class EvidenceCustodyEventSerializer(serializers.ModelSerializer):
    holder_username = serializers.CharField(source="holder.username", read_only=True)

    class Meta:
        model = EvidenceCustodyEvent
        fields = (
            "id",
            "event_type",
            "holder_username",
            "taken_at",
            "released_at",
            "notes",
        )


class EvidenceSerializer(serializers.ModelSerializer):
    current_custodian_username = serializers.CharField(source="current_custodian.username", read_only=True)
    file_meta = EvidenceFileSerializer(read_only=True)
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Evidence
        fields = (
            "id",
            "title",
            "description",
            "status",
            "classification",
            "current_custodian",
            "current_custodian_username",
            "workspace_id",
            "file_meta",
            "latest_version",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "current_custodian",
            "created_at",
            "updated_at",
        )

    def get_latest_version(self, obj) -> dict | None:
        latest = obj.versions.order_by("-version_number").first()
        if latest:
            return EvidenceVersionSerializer(latest).data
        return None


class EvidenceCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=True)
    investigation_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Evidence
        fields = (
            "title",
            "description",
            "classification",
            "workspace",
            "file",
            "investigation_id",
        )
        extra_kwargs = {
            "title": {"required": True},
            "workspace": {"required": True},
            "classification": {"required": False},
        }


class CustodyTransferSerializer(serializers.Serializer):
    new_custodian_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=True, source="new_custodian"
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")
