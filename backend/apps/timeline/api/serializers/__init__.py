from rest_framework import serializers

from ...models import Timeline, TimelineEvent, EventCluster, TimelineSnapshot

class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")

class TimelineSerializer(serializers.ModelSerializer):
    events = TimelineEventSerializer(many=True, read_only=True)

    class Meta:
        model = Timeline
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")

class EventClusterSerializer(serializers.ModelSerializer):
    events = TimelineEventSerializer(many=True, read_only=True)

    class Meta:
        model = EventCluster
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")

class TimelineSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineSnapshot
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")
