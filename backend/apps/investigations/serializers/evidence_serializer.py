from rest_framework import serializers

from ..models.evidence import Evidence
from ..validators.evidence_validator import (
    validate_file_size,
    validate_mime_type,
)


class EvidenceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Evidence.
    Delegates all validation to stateless validators; persistence is handled by the service layer.
    """

    class Meta:
        model = Evidence
        fields = ("title", "description", "file", "status")
        extra_kwargs = {"status": {"required": False}}

    def validate_file(self, value):
        validate_file_size(value)
        validate_mime_type(value)
        # Optional checksum & filename validation could be performed elsewhere (e.g., in EvidenceFile)
        return value

    def validate(self, attrs):
        # Cross‑field validation placeholder
        return attrs

class EvidenceDetailSerializer(serializers.ModelSerializer):
    """Read‑only detailed representation of an Evidence object."""

    class Meta:
        model = Evidence
        fields = (
            "id",
            "title",
            "description",
            "file",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

class EvidenceListSerializer(serializers.ModelSerializer):
    """Compact list view for Evidence objects."""

    class Meta:
        model = Evidence
        fields = ("id", "title", "status", "created_at")
        read_only_fields = fields
