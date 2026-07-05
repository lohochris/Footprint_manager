import pytest
import uuid
from decimal import Decimal
from backend.apps.graph.dtos import NodeDTO
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO, NodeCentralityDTO
from backend.apps.intelligence.models.enums import FactorType, RecommendationType, Severity
from backend.apps.intelligence.models import WatchlistEntry
from backend.apps.intelligence.services.risk_strategies import (
    CentralityStrategy,
    ConfidenceStrategy,
    WatchlistProximityStrategy,
)
from backend.apps.intelligence.services.recommendation_strategies import (
    IsolatedEntityStrategy,
    HighCentralityStrategy,
    SuspiciousClusterStrategy,
    MissingEvidenceStrategy,
)
from backend.apps.intelligence.dto.risk import RiskAssessmentDTO, EntityRiskDTO

pytestmark = pytest.mark.django_db

class TestRiskStrategies:
    def test_centrality_strategy(self):
        strategy = CentralityStrategy()
        node = NodeDTO(id=uuid.uuid4(), tenant_id="tenant_1", workspace_id="workspace_1", node_type="entity", label="Person", metadata={})
        metrics = NodeCentralityDTO(node_id=node.id, degree=Decimal("0.8"))
        analytics = AnalyticsResultDTO(tenant_id="tenant_1", workspace_id="workspace_1")

        factors = strategy.evaluate(node, metrics, analytics, {})
        assert len(factors) == 1
        assert factors[0].factor_type == FactorType.HIGH_CENTRALITY
        assert factors[0].weight_applied == Decimal("0.20")

    def test_confidence_strategy(self):
        strategy = ConfidenceStrategy()
        node = NodeDTO(id=uuid.uuid4(), tenant_id="tenant_1", workspace_id="workspace_1", node_type="entity", label="Person", metadata={}, confidence=Decimal("0.4"))
        metrics = NodeCentralityDTO(node_id=node.id)
        analytics = AnalyticsResultDTO(tenant_id="tenant_1", workspace_id="workspace_1")

        factors = strategy.evaluate(node, metrics, analytics, {})
        assert len(factors) == 1
        assert factors[0].factor_type == FactorType.CONFIDENCE_ADJUSTMENT
        assert factors[0].weight_applied == Decimal("-0.10")

    def test_watchlist_proximity_strategy(self, db):
        strategy = WatchlistProximityStrategy()
        node = NodeDTO(id=uuid.uuid4(), tenant_id="tenant_1", workspace_id="workspace_1", node_type="entity", label="BadGuy", metadata={})
        metrics = NodeCentralityDTO(node_id=node.id)
        analytics = AnalyticsResultDTO(tenant_id="tenant_1", workspace_id="workspace_1")

        class MockWatchlist:
            entity_value = "BadGuy"

        context = {"watchlists": [MockWatchlist()]}
        factors = strategy.evaluate(node, metrics, analytics, context)

        assert len(factors) == 1
        assert factors[0].factor_type == FactorType.WATCHLIST_PROXIMITY
        assert factors[0].weight_applied == Decimal("0.50")

class TestRecommendationStrategies:
    def test_isolated_entity_strategy(self):
        strategy = IsolatedEntityStrategy()
        node_id = uuid.uuid4()
        metrics = NodeCentralityDTO(node_id=node_id, degree=Decimal("0.0"))
        analytics = AnalyticsResultDTO(tenant_id="tenant_1", workspace_id="workspace_1", node_metrics={node_id: metrics})
        risk = RiskAssessmentDTO(tenant_id="tenant_1", workspace_id="workspace_1")

        recs = strategy.generate(
            tenant_id="tenant_1",
            workspace_id="workspace_1",
            nodes=[NodeDTO(id=node_id, tenant_id="tenant_1", workspace_id="workspace_1", node_type="entity", label="Person", metadata={})],
            edges=[],
            analytics=analytics,
            risk=risk,
            context={}
        )
        assert len(recs) == 1
        assert recs[0].target_node_id == node_id
        assert recs[0].recommendation_type == RecommendationType.ISOLATED_ENTITY
        assert recs[0].severity == Severity.LOW

    def test_high_centrality_strategy(self):
        strategy = HighCentralityStrategy()
        node_id = uuid.uuid4()
        metrics = NodeCentralityDTO(node_id=node_id, degree=Decimal("0.9"))
        analytics = AnalyticsResultDTO(tenant_id="tenant_1", workspace_id="workspace_1", node_metrics={node_id: metrics})
        risk = RiskAssessmentDTO(tenant_id="tenant_1", workspace_id="workspace_1")

        recs = strategy.generate(
            tenant_id="tenant_1",
            workspace_id="workspace_1",
            nodes=[NodeDTO(id=node_id, tenant_id="tenant_1", workspace_id="workspace_1", node_type="entity", label="Person", metadata={})],
            edges=[],
            analytics=analytics,
            risk=risk,
            context={}
        )
        assert len(recs) == 1
        assert recs[0].target_node_id == node_id
        assert recs[0].recommendation_type == RecommendationType.HIGH_CENTRALITY
        assert recs[0].severity == Severity.HIGH
