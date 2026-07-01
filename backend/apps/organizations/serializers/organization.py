from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models.organization import Organization
from ..services.organization_service import OrganizationService

User = get_user_model()
from ..validators import (
    validate_organization_slug_unique,
)


class OrganizationSerializer(serializers.ModelSerializer):
    """Read‑only representation of an Organization."""

    class Meta(serializers.ModelSerializer.Meta):
        model = Organization  # type: ignore[assignment]
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo",
            "website",
            "industry",
            "country",
            "timezone",
            "subscription_tier",
            "status",
            "owner",
            "settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

class OrganizationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=150)
    description = serializers.CharField(allow_blank=True, required=False)
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    settings = serializers.JSONField(required=False)

    def validate_slug(self, value):
        validate_organization_slug_unique(value)
        return value

    def create(self, validated_data: dict) -> dict:
        """Return validated data; view will invoke service layer."""
        return validated_data

class OrganizationUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    logo = serializers.ImageField(required=False, allow_null=True)
    website = serializers.URLField(required=False, allow_null=True)
    industry = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=2, required=False, allow_blank=True)
    timezone = serializers.CharField(max_length=50, required=False)
    subscription_tier = serializers.CharField(max_length=50, required=False)
    status = serializers.ChoiceField(choices=[(c, c) for c in ["active", "inactive", "suspended"]], required=False)
    settings = serializers.JSONField(required=False)

    def update(self, instance, validated_data):
        return OrganizationService.update_organization(
            organization=instance,
            **validated_data,
        )
