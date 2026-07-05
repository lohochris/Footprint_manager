from rest_framework import serializers
from ..models import Integration, Subscription, IntegrationEvent

class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = ['id', 'name', 'provider', 'status', 'is_enabled', 'configuration', 'created_at']
        read_only_fields = ['id', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'integration', 'event_name', 'is_active']
        read_only_fields = ['id']

class IntegrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationEvent
        fields = ['id', 'direction', 'event_type', 'status', 'idempotency_key', 'created_at']
        read_only_fields = ['id', 'created_at']
