from rest_framework import serializers
from ..models.channel import RealtimeChannel
from ..models.connection import Connection
from ..models.subscription import Subscription
from ..models.presence import Presence
from ..models.audit import StreamAudit

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealtimeChannel
        fields = ['id', 'channel_type', 'resource_identifier', 'permissions_required']
        read_only_fields = ['id']

class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['id', 'protocol', 'session_id', 'client_metadata', 'state', 'last_heartbeat_at']
        read_only_fields = ['id', 'session_id', 'state', 'last_heartbeat_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'channel', 'connection', 'status', 'expires_at']
        read_only_fields = ['id', 'status']

class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ['user', 'status', 'last_heartbeat_at', 'active_workspace_id', 'connected_devices']
        read_only_fields = ['user', 'last_heartbeat_at']

class StreamAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamAudit
        fields = ['id', 'connection', 'action', 'status', 'details', 'created_at']
        read_only_fields = fields
