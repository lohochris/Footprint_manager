from rest_framework import serializers
from backend.apps.identity.models import (
    Identity,
    IdentityAttribute,
    IdentityRelationship,
    IdentityMatch,
    IdentityMergeHistory,
)


class IdentityAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityAttribute
        fields = [
            "id",
            "type",
            "key",
            "value",
            "normalized_value",
            "confidence",
            "evidence_references",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "normalized_value", "created_at", "updated_at"]


class IdentityRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityRelationship
        fields = [
            "id",
            "source_identity",
            "target_identity",
            "type",
            "confidence",
            "source",
            "evidence_references",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class IdentitySerializer(serializers.ModelSerializer):
    attributes = IdentityAttributeSerializer(many=True, read_only=True)
    relationships_from = IdentityRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = Identity
        fields = [
            "id",
            "entity_type",
            "label",
            "confidence_score",
            "confidence_details",
            "source",
            "workspace",
            "attributes",
            "relationships_from",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "confidence_score", "confidence_details", "created_at", "updated_at"]


class IdentityCreateSerializer(serializers.ModelSerializer):
    attributes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
        write_only=True,
        help_text="Optional starting attributes for the identity",
    )

    class Meta:
        model = Identity
        fields = [
            "entity_type",
            "label",
            "source",
            "workspace",
            "attributes",
        ]


class IdentityMatchSerializer(serializers.ModelSerializer):
    candidate_a = IdentitySerializer(read_only=True)
    candidate_b = IdentitySerializer(read_only=True)

    class Meta:
        model = IdentityMatch
        fields = [
            "id",
            "candidate_a",
            "candidate_b",
            "confidence",
            "matching_strategy",
            "review_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "confidence", "matching_strategy", "created_at", "updated_at"]


class IdentityMergeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityMergeHistory
        fields = [
            "id",
            "source_identity_id",
            "target_identity",
            "action",
            "merge_metadata",
            "reviewer",
            "created_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at"]
