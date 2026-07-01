# backend/intelligence/router.py
"""AI Provider Router.

Selects the appropriate :class:`AIProvider` for an incoming :class:`AIRequest`.
Contains no business logic, no HTTP calls, no SDKs, and no external dependencies.
"""

from __future__ import annotations

from intelligence.providers.base import AIProvider
from intelligence.providers.registry import ProviderRegistry
from intelligence.providers.registry import _registry as _global_registry
from intelligence.providers.request import AIRequest


class ProviderNotFoundError(Exception):
    """Raised when a named provider does not exist in the registry."""


class NoProviderAvailableError(Exception):
    """Raised when no capable provider is available and no default is registered."""


class Router:
    """Selects an AI provider class for a given :class:`AIRequest`.

    Selection strategy (in order):

    1. **Explicit** — if ``request.metadata["provider"]`` is set, select the
       provider with that name.  Raises :exc:`ProviderNotFoundError` if not
       registered.
    2. **Capability-first** — filter all registered providers by whether they
       support ``request.task``.  Return the highest-priority capable provider
       (lowest ``priority`` value wins, per the registry's ordering).
    3. **Default fallback** — if no provider supports the task, return the
       registry's default (first by priority).
    4. **Empty registry** — raise :exc:`NoProviderAvailableError`.

    The router returns a **class** (not an instance).  Instantiation is the
    caller's responsibility so that constructor arguments can be supplied if
    needed.

    Parameters
    ----------
    registry:
        The :class:`ProviderRegistry` to query.  Defaults to the global
        singleton populated by the Sprint 3B.7 provider registrations.
    """

    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self._registry: ProviderRegistry = (
            registry if registry is not None else _global_registry
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def select(self, request: AIRequest) -> type[AIProvider]:
        """Return the provider class best suited for *request*.

        Parameters
        ----------
        request:
            The incoming AI request.

        Returns
        -------
        type[AIProvider]
            A concrete provider class.

        Raises
        ------
        ProviderNotFoundError
            If ``request.metadata["provider"]`` is set but no matching
            provider is registered.
        NoProviderAvailableError
            If the registry is empty or no provider can be selected.
        """
        provider_name: str | None = (
            request.metadata.get("provider")  # type: ignore[union-attr]
            if request.metadata
            else None
        )
        if provider_name:
            return self._select_by_name(provider_name)
        return self._select_by_task(request.task)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _select_by_name(self, name: str) -> type[AIProvider]:
        """Select a provider by explicit name."""
        provider_cls = self._registry.get(name)
        if provider_cls is None:
            raise ProviderNotFoundError(
                f"Provider '{name}' is not registered."
            )
        return provider_cls

    def _select_by_task(self, task: str) -> type[AIProvider]:
        """Select the highest-priority provider that supports *task*."""
        candidates = [
            p for p in self._registry.list()
            if p().supports(task)
        ]
        if candidates:
            return candidates[0]

        # Fallback: registry default (first by priority regardless of task)
        default = self._registry.default()
        if default is not None:
            return default

        raise NoProviderAvailableError(
            f"No provider available for task '{task}' "
            "and no default provider is registered."
        )
