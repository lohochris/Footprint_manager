from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.apps.decision_engine.api.permissions import (
    CanManagePolicy,
    CanPublishPolicy,
    CanViewAudit,
    CanViewDecision,
)
from backend.apps.decision_engine.dto import EvaluationInputDTO
from backend.apps.decision_engine.selectors import DecisionSelector, PolicySelector
from backend.apps.decision_engine.services import DecisionService, PolicyService


class PolicyViewSet(viewsets.ViewSet):
    permission_classes = [CanManagePolicy]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.policy_selector = PolicySelector()
        self.policy_service = PolicyService()

    def list(self, request):
        tenant_id = request.user.tenant_id
        policies = self.policy_selector.list_policies(tenant_id)
        # Assuming we have a standard serializer or just return dicts for MVP
        return Response([p.__dict__ for p in policies])

    def retrieve(self, request, pk=None):
        tenant_id = request.user.tenant_id
        policy = self.policy_selector.get_policy_detail(tenant_id, pk)
        if not policy:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Serialize rules correctly
        policy_dict = policy.__dict__.copy()
        policy_dict["rules"] = [r.__dict__ for r in policy.rules]
        return Response(policy_dict)

    @action(detail=True, methods=["post"], permission_classes=[CanPublishPolicy])
    def publish(self, request, pk=None):
        tenant_id = request.user.tenant_id
        success = self.policy_service.publish_policy(tenant_id, pk, str(request.user.id))
        if success:
            return Response({"status": "published"})
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def simulate(self, request):
        """Simulate policy execution without side-effects."""
        tenant_id = request.user.tenant_id
        payload = request.data.get("payload", {})
        event_type = request.data.get("event_type", "simulation")

        input_dto = EvaluationInputDTO(
            tenant_id=tenant_id,
            event_type=event_type,
            payload=payload,
            trace_identifier="sim-" + str(request.user.id),
        )

        decision_service = DecisionService()
        result_dto = decision_service.coordinator.evaluate(input_dto)

        response_data = {
            "decision": result_dto.decision.__dict__,
            "recommendations": [r.__dict__ for r in result_dto.recommendations],
            "matched_rules": result_dto.matched_rule_ids,
            "applied_policies": result_dto.applied_policy_ids,
        }
        return Response(response_data)


class DecisionViewSet(viewsets.ViewSet):
    permission_classes = [CanViewDecision]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.decision_selector = DecisionSelector()

    def retrieve(self, request, pk=None):
        tenant_id = request.user.tenant_id
        decision = self.decision_selector.get_decision_detail(tenant_id, pk)
        if not decision:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(decision.__dict__)
