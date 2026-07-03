"""Policy engine for evaluating AI execution requests."""

from typing import NamedTuple, Any, Dict
from intelligence.policies.execution_policy import ExecutionPolicy
from intelligence.providers.base import AIProvider
from intelligence.providers.request import AIRequest
from intelligence.provider_state import ProviderLifecycleState

class EvaluationResult(NamedTuple):
    allowed: bool
    reason: str | None = None
    diagnostics: Dict[str, Any] | None = None

class PolicyEngine:
    """Evaluates execution policies against execution contexts."""

    def evaluate(
        self,
        request: AIRequest,
        provider: AIProvider,
        policy: ExecutionPolicy,
    ) -> EvaluationResult:
        """Evaluate if *provider* is allowed to execute the given *request* under *policy*.

        Accepts the request, provider, and execution policy as context parameters.
        """
        # Check provider lifecycle state
        state = getattr(provider, "lifecycle_state", ProviderLifecycleState.ACTIVE)
        if state != ProviderLifecycleState.ACTIVE:
            return EvaluationResult(
                allowed=False,
                reason=f"Provider lifecycle state is '{state}', expected '{ProviderLifecycleState.ACTIVE}'.",
                diagnostics={"lifecycle_state": state, "allowed": False}
            )

        # Check provider health if required by policy
        if policy.health_required:
            try:
                health = provider.health_check()
                if not health.healthy:
                    return EvaluationResult(
                        allowed=False,
                        reason=f"Provider is unhealthy: {health.message}",
                        diagnostics={"healthy": False, "health_message": health.message, "allowed": False}
                    )
            except Exception as exc:
                return EvaluationResult(
                    allowed=False,
                    reason=f"Provider health check raised exception: {exc}",
                    diagnostics={"healthy": False, "health_error": str(exc), "allowed": False}
                )

        # Check required provider constraint if specified
        provider_name = getattr(provider, "name", provider.__class__.__name__)
        if policy.required_provider and provider_name != policy.required_provider:
            return EvaluationResult(
                allowed=False,
                reason=f"Provider name '{provider_name}' does not match required provider '{policy.required_provider}'.",
                diagnostics={"required_provider": policy.required_provider, "allowed": False}
            )

        return EvaluationResult(
            allowed=True,
            diagnostics={"allowed": True, "lifecycle_state": state, "healthy": True}
        )
