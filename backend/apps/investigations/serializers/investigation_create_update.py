from django.core.exceptions import ValidationError
from rest_framework import serializers

from ..models.investigation import Investigation
from ..validators.investigation_validator import validate_priority, validate_tags


class InvestigationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Investigation objects.
    Validation is delegated to domain validators; business logic stays in the service layer.
    """

    class Meta:
        model = Investigation
        fields = (
            "title",
            "description",
            "status",
            "priority",
            "classification",
            "visibility",
            "risk_level",
            "tags",
            "metadata",
        )
        extra_kwargs = {
            "status": {"required": False},
            "priority": {"required": False},
            "classification": {"required": False},
            "visibility": {"required": False},
            "risk_level": {"required": False},
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

    def validate(self, attrs):
        # additional cross‑field validation can be added here if needed
        return attrs
