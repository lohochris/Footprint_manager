import pytest
from unittest.mock import MagicMock
from backend.apps.intelligence.engine.intelligence_engine import IntelligenceEngine
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO
from backend.apps.intelligence.dto.risk import RiskAssessmentDTO
from backend.apps.intelligence.dto.recommendation import RecommendationResultDTO

def test_intelligence_engine_orchestration():
    mock_analytics_service = MagicMock()
    mock_risk_service = MagicMock()
    mock_recommendation_service = MagicMock()

    mock_analytics_result = AnalyticsResultDTO(tenant_id="t1", workspace_id="w1")
    mock_risk_result = RiskAssessmentDTO(tenant_id="t1", workspace_id="w1")
    mock_recommendation_result = RecommendationResultDTO()

    mock_analytics_service.analyze_graph.return_value = mock_analytics_result
    mock_risk_service.assess_risk.return_value = mock_risk_result
    mock_recommendation_service.generate_recommendations.return_value = mock_recommendation_result

    engine = IntelligenceEngine(
        analytics_service=mock_analytics_service,
        risk_service=mock_risk_service,
        recommendation_service=mock_recommendation_service,
    )

    result = engine.process_graph("t1", "w1", [], [], {"test": True})

    # Verify calls
    mock_analytics_service.analyze_graph.assert_called_once_with(
        tenant_id="t1", workspace_id="w1", nodes=[], edges=[]
    )

    mock_risk_service.assess_risk.assert_called_once_with(
        tenant_id="t1", workspace_id="w1", nodes=[], analytics=mock_analytics_result, context={"test": True}
    )

    mock_recommendation_service.generate_recommendations.assert_called_once_with(
        tenant_id="t1", workspace_id="w1", nodes=[], edges=[], analytics=mock_analytics_result, risk=mock_risk_result, context={"test": True}
    )

    assert result["analytics"] == mock_analytics_result
    assert result["risk"] == mock_risk_result
    assert result["recommendations"] == mock_recommendation_result
