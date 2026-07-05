import pytest
import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from backend.apps.organizations.models.organization import Organization
from backend.apps.organizations.models.workspace import Workspace
from backend.apps.intelligence.models import (
    EntityScore,
    RiskFactor,
    IntelligenceRecommendation,
    WatchlistEntry,
    InvestigationPriority,
    AnalyticsSnapshot,
)
from backend.apps.intelligence.models.enums import (
    FactorType,
    RecommendationType,
    Severity,
    RecommendationStatus,
    EntityType,
    MatchMode,
)

User = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    return User.objects.create(
        email="test@example.com",
    )

@pytest.fixture
def tenant(user):
    return Organization.objects.create(name="Test Tenant", slug="test-tenant", owner=user)

@pytest.fixture
def workspace(tenant):
    return Workspace.objects.create(
        name="Test Workspace",
        slug="test-workspace",
        organization=tenant,
    )

class TestEntityScore:
    def test_create_entity_score(self, tenant, user, workspace):
        score = EntityScore.objects.create(
            tenant_id=tenant.id,
            owner=user,
            workspace=workspace,
            node_id=uuid.uuid4(),
            risk_score=Decimal("0.8500"),
            confidence_score=Decimal("0.9000"),
            centrality_metrics={"degree": 0.8},
            explanation={"reasons": ["high centrality"]},
            score_version="1.0.0",
        )
        assert score.id is not None
        assert score.risk_score == Decimal("0.8500")
        assert score.confidence_score == Decimal("0.9000")
        assert "degree" in score.centrality_metrics

class TestRiskFactor:
    def test_create_risk_factor(self, tenant, user, workspace):
        score = EntityScore.objects.create(
            tenant_id=tenant.id,
            owner=user,
            workspace=workspace,
            node_id=uuid.uuid4(),
        )
        factor = RiskFactor.objects.create(
            tenant_id=tenant.id,
            owner=user,
            entity_score=score,
            factor_type=FactorType.HIGH_CENTRALITY,
            weight_applied=Decimal("0.2000"),
            description="Highly central node",
        )
        assert factor.id is not None
        assert factor.factor_type == FactorType.HIGH_CENTRALITY
        assert factor.weight_applied == Decimal("0.2000")
        assert factor.entity_score == score

class TestIntelligenceRecommendation:
    def test_create_recommendation(self, tenant, user, workspace):
        rec = IntelligenceRecommendation.objects.create(
            tenant_id=tenant.id,
            owner=user,
            workspace=workspace,
            target_node_id=uuid.uuid4(),
            recommendation_type=RecommendationType.SUSPICIOUS_CLUSTER,
            severity=Severity.CRITICAL,
            reasoning="Cluster of high risk nodes",
            status=RecommendationStatus.OPEN,
        )
        assert rec.id is not None
        assert rec.recommendation_type == RecommendationType.SUSPICIOUS_CLUSTER
        assert rec.severity == Severity.CRITICAL

class TestWatchlistEntry:
    def test_create_watchlist_entry(self, tenant, user):
        entry = WatchlistEntry.objects.create(
            tenant_id=tenant.id,
            owner=user,
            entity_value="192.168.1.1",
            entity_type=EntityType.IP_ADDRESS,
            match_mode=MatchMode.EXACT,
            risk_level=Severity.HIGH,
        )
        assert entry.id is not None
        assert entry.entity_value == "192.168.1.1"

class TestInvestigationPriority:
    def test_create_investigation_priority(self, tenant, user, workspace):
        priority = InvestigationPriority.objects.create(
            tenant_id=tenant.id,
            owner=user,
            workspace=workspace,
            investigation_id=uuid.uuid4(),
            aggregate_risk_score=Decimal("0.7500"),
            flagged_entities_count=3,
        )
        assert priority.id is not None
        assert priority.flagged_entities_count == 3

class TestAnalyticsSnapshot:
    def test_create_analytics_snapshot(self, tenant, user, workspace):
        snapshot = AnalyticsSnapshot.objects.create(
            tenant_id=tenant.id,
            owner=user,
            workspace=workspace,
            graph_snapshot_id=uuid.uuid4(),
            statistics={"nodes": 10, "edges": 15},
        )
        assert snapshot.id is not None
        assert snapshot.statistics["nodes"] == 10
