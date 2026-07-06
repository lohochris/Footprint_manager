from rest_framework import serializers
from backend.apps.accounts.models import User, UserProfile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id", "biography", "job_title", "department", "country",
            "city", "address", "avatar", "timezone", "language",
            "theme_preference", "notification_preferences", "accessibility_preferences"
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "is_active",
            "account_status", "date_joined", "profile"
        ]
        read_only_fields = ["id", "email", "is_active", "account_status", "date_joined"]
