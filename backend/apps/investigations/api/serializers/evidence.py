from rest_framework import serializers
from backend.apps.investigations.models import EvidenceReference


class EvidenceReferenceSerializer(serializers.ModelSerializer):
    """Serializer for the EvidenceReference model."""

    linked_by_username = serializers.CharField(source="linked_by.username", read_only=True)

    class Meta:
        model = EvidenceReference
        fields = (
            "id",
            "investigation",
            "reference_type",
            "source",
            "external_identifier",
            "uri",
            "hash_value",
            "summary",
            "metadata",
            "linked_by",
            "linked_by_username",
            "linked_at",
        )
        read_only_fields = ("id", "investigation", "linked_by", "linked_at")
