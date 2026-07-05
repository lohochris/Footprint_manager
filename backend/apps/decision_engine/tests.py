import pytest

from backend.apps.decision_engine.dto import EvaluationInputDTO, RuleDTO
from backend.apps.decision_engine.providers.internal import InternalRuleProvider


def test_internal_rule_provider_simple_condition():
    provider = InternalRuleProvider()
    
    rule = RuleDTO(
        id="rule-1",
        name="Test Rule",
        description="",
        conditions={
            "allOf": [
                {"field": "risk_score", "operator": ">", "value": 80}
            ]
        },
        expression="",
        evaluation_order=1,
        is_active=True,
    )
    
    input_data = EvaluationInputDTO(
        tenant_id="tenant-1",
        event_type="RiskScoreCalculated",
        payload={"risk_score": 85},
        trace_identifier="test-trace",
    )
    
    # Should match
    assert provider.evaluate_rule(rule, input_data) is True
    
    # Should not match
    input_data_fail = EvaluationInputDTO(
        tenant_id="tenant-1",
        event_type="RiskScoreCalculated",
        payload={"risk_score": 50},
        trace_identifier="test-trace-2",
    )
    assert provider.evaluate_rule(rule, input_data_fail) is False


def test_internal_rule_provider_nested_value():
    provider = InternalRuleProvider()
    
    rule = RuleDTO(
        id="rule-1",
        name="Nested Rule",
        description="",
        conditions={
            "allOf": [
                {"field": "report.confidence", "operator": ">=", "value": 0.9}
            ]
        },
        expression="",
        evaluation_order=1,
        is_active=True,
    )
    
    input_data = EvaluationInputDTO(
        tenant_id="tenant-1",
        event_type="AIReportGenerated",
        payload={"report": {"confidence": 0.95}},
        trace_identifier="test-trace",
    )
    
    assert provider.evaluate_rule(rule, input_data) is True
