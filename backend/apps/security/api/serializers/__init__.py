from rest_framework import serializers

from ...models import (
    APIKey,
    SecurityEvent,
    SecurityPolicy,
    SecuritySession,
    TrustedDevice,
)


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization", "key_hash")


class TrustedDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedDevice
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")


class SecuritySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecuritySession
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")


class SecurityPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityPolicy
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")
