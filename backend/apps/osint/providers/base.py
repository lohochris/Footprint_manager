# backend/apps/osint/providers/base.py
"""Abstract OSINT Discovery Provider interface.

This module defines the behavioural contract that every concrete OSINT
provider must satisfy.  It intentionally contains no network calls, no
vendor logic, and no Django ORM imports — mirroring the discipline of
``backend.intelligence.providers.base.AIProvider``.

Provider interface (seven methods)
-----------------------------------
Lifecycle
    ``initialize()``       – load credentials / warm up connections.
    ``health_check()``     – return a ``DiscoveryHealthStatus`` snapshot.

Capability contract
    ``capabilities()``     – return the list of DiscoveryCapability values.
    ``supports()``         – return True if a given capability is offered.

Execution contract
    ``validate_target()``  – raise ``ValidationError`` for invalid input.
    ``discover()``         – execute the query; return raw result dicts.
    ``normalize()``        – map one raw dict to canonical schema dict.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .provider_metadata import DiscoveryHealthStatus


class BaseDiscoveryProvider(ABC):
    """Abstract base class for all OSINT Discovery providers.

    Concrete implementations live in separate modules and register
    themselves via ``backend.apps.osint.providers.registry``.

    Class attributes
    ----------------
    name:
        Unique machine-readable provider slug.  Must match the
        ``DiscoveryProvider.name`` value in the database catalogue.
    version:
        Semantic version string of the provider implementation.
    description:
        Human-readable summary of what the provider discovers.
    priority:
        Integer routing priority (lower = higher priority).  Used by
        ``DiscoveryProviderRegistry.list()`` to return providers in
        deterministic order.
    """

    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    priority: int = 100

    # -------------------------------------------------------------------------
    # Lifecycle methods
    # -------------------------------------------------------------------------

    @abstractmethod
    def initialize(self) -> None:
        """Perform any required initialisation (e.g. load credentials).

        Must be safe to call multiple times.  Implementations should raise
        ``RuntimeError`` if initialisation fails irreversibly.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> DiscoveryHealthStatus:
        """Return a structured health snapshot for this provider.

        The returned snapshot is stored on the ``DiscoveryProvider`` model
        record (``last_health_status`` / ``last_health_message``) by the
        ``DiscoveryJobService`` after each probe.
        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Capability contract
    # -------------------------------------------------------------------------

    @abstractmethod
    def capabilities(self) -> list[str]:
        """Return the list of ``DiscoveryCapability`` values this provider offers.

        Values must correspond to members of
        ``backend.apps.osint.enums.DiscoveryCapability``.
        """
        raise NotImplementedError

    @abstractmethod
    def supports(self, capability: str) -> bool:
        """Return ``True`` if this provider supports the given ``capability``.

        Parameters
        ----------
        capability:
            A ``DiscoveryCapability`` value string.
        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Execution contract
    # -------------------------------------------------------------------------

    @abstractmethod
    def validate_target(self, input_data: dict) -> None:
        """Validate the query payload before execution.

        Raise ``django.core.exceptions.ValidationError`` (or a plain
        ``ValueError``) if ``input_data`` is missing required keys or
        contains invalid values.

        Parameters
        ----------
        input_data:
            The same dict that will be passed to ``discover()``.
        """
        raise NotImplementedError

    @abstractmethod
    def discover(self, input_data: dict) -> list[dict]:
        """Execute the discovery query and return raw provider results.

        Concrete implementations perform the actual external API call.
        Each dict in the returned list is an opaque provider-specific
        payload that will subsequently be passed to ``normalize()``.

        Parameters
        ----------
        input_data:
            Validated query payload (pre-cleared by ``validate_target()``).

        Returns
        -------
        list[dict]
            Zero or more raw result dicts from the upstream provider.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: dict) -> dict:
        """Map a single raw provider result to the canonical schema.

        The canonical schema is provider-agnostic and governs the
        ``DiscoveryResult.normalised_data`` field.  Sprint 6 does not
        mandate a fixed schema; providers document their own output
        structure.  A common schema will be formalised in the Identity
        Resolution sprint.

        Parameters
        ----------
        raw:
            A single element from the list returned by ``discover()``.

        Returns
        -------
        dict
            Normalised representation suitable for storage in
            ``DiscoveryResult.normalised_data``.
        """
        raise NotImplementedError
