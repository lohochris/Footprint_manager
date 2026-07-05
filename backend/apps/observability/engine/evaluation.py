import uuid
from ..models import AlertRule, Alert
from ..repositories import AlertRepository
from ..providers.registry import ProviderRegistry

class EvaluationEngine:
    @staticmethod
    def evaluate_metric(tenant_id: uuid.UUID, metric_name: str, current_value: float) -> None:
        """
        Evaluates a metric against all active rules.
        """
        rules = AlertRule.objects.filter(tenant_id=tenant_id, metric_name=metric_name, is_active=True)

        for rule in rules:
            triggered = False
            if rule.condition == ">" and current_value > rule.threshold or rule.condition == ">=" and current_value >= rule.threshold or rule.condition == "<" and current_value < rule.threshold or rule.condition == "<=" and current_value <= rule.threshold or rule.condition == "==" and current_value == rule.threshold:
                triggered = True

            if triggered:
                # Create alert
                alert = AlertRepository.create_alert(
                    tenant_id=tenant_id,
                    severity=rule.severity,
                    source="evaluation_engine",
                    details={"metric": metric_name, "value": current_value, "threshold": rule.threshold},
                    rule_id=rule.id
                )

                # In a real setup, dispatch via AlertProvider here.
                # For Sprint 15, we'll log it.
                logger = ProviderRegistry.get_logging_provider()
                logger.log(tenant_id, "WARNING", f"Alert triggered for {metric_name}", {"alert_id": str(alert.id)})
