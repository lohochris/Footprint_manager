from rest_framework import serializers

class MetricSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    value = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    source = serializers.CharField()  # type: ignore[assignment]
    labels = serializers.JSONField()

class HealthSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    component = serializers.CharField()
    status = serializers.CharField()
    response_time_ms = serializers.IntegerField()
    last_check = serializers.DateTimeField()
    failure_reason = serializers.CharField()

class AlertSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    severity = serializers.CharField()
    source = serializers.CharField()  # type: ignore[assignment]
    trigger_time = serializers.DateTimeField()
    resolved_at = serializers.DateTimeField(allow_null=True)
    details = serializers.JSONField()

class TraceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    trace_id = serializers.CharField()
    span_id = serializers.CharField()
    parent_span_id = serializers.CharField(allow_null=True)
    name = serializers.CharField()
    duration_ms = serializers.IntegerField(allow_null=True)
    status = serializers.CharField()

class DiagnosticSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    captured_at = serializers.DateTimeField()
    component_health = serializers.JSONField()
    active_connections = serializers.IntegerField()

class DashboardSerializer(serializers.Serializer):
    active_alerts = serializers.IntegerField()
    failed_integrations_24h = serializers.FloatField()
    ai_tokens_24h = serializers.FloatField()
