from rest_framework import permissions


class DecisionEnginePermission(permissions.BasePermission):
    """
    Base permission for Decision Engine.
    In a real system, this integrates with the central RBAC provider.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanManagePolicy(DecisionEnginePermission):
    def has_permission(self, request, view):
        # MVP: Check if user has policy.manage
        # return request.user.has_perm("decision_engine.policy.manage")
        return super().has_permission(request, view)


class CanPublishPolicy(DecisionEnginePermission):
    def has_permission(self, request, view):
        # return request.user.has_perm("decision_engine.policy.publish")
        return super().has_permission(request, view)


class CanViewDecision(DecisionEnginePermission):
    def has_permission(self, request, view):
        # return request.user.has_perm("decision_engine.decision.view")
        return super().has_permission(request, view)


class CanExecuteRecommendation(DecisionEnginePermission):
    def has_permission(self, request, view):
        # return request.user.has_perm("decision_engine.recommendation.execute")
        return super().has_permission(request, view)


class CanViewAudit(DecisionEnginePermission):
    def has_permission(self, request, view):
        # return request.user.has_perm("decision_engine.audit.view")
        return super().has_permission(request, view)
