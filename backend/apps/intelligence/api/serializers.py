from rest_framework import serializers
from backend.apps.intelligence.models import (
    EntityScore,
    RiskFactor,
    IntelligenceRecommendation,
    WatchlistEntry,
    InvestigationPriority,
)

class RiskFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskFactor
        fields = ["id", "factor_type", "weight_applied", "description"]


class EntityScoreSerializer(serializers.ModelSerializer):
    factors = RiskFactorSerializer(many=True, read_only=True)

    class Meta:
        model = EntityScore
        fields = [
            "id",
            "node_id",
            "risk_score",
            "confidence_score",
            "centrality_metrics",
            "explanation",
            "score_version",
            "factors",
            "created_at",
            "updated_at",
        ]


class IntelligenceRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntelligenceRecommendation
        fields = [
            "id",
            "target_node_id",
            "recommendation_type",
            "severity",
            "reasoning",
            "status",
            "created_at",
            "updated_at",
        ]


class WatchlistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistEntry
        fields = [
            "id",
            "entity_value",
            "entity_type",
            "match_mode",
            "risk_level",
            "created_at",
            "updated_at",
        ]


class InvestigationPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestigationPriority
        fields = [
            "id",
            "investigation_id",
            "aggregate_risk_score",
            "flagged_entities_count",
            "created_at",
            "updated_at",
        ]
