"""
Shared permission policy interfaces for Footprint Manager.

This module defines the abstract contract that all domain-specific permission
policies must implement.  Concrete policies live inside their respective app
packages (e.g. ``apps.rbac.policies``).

The interface deliberately avoids Django-specific coupling so that policies
can be unit-tested without an HTTP request context.

Usage::

    from shared.permissions import BasePermissionPolicy

    class InvestigationPolicy(BasePermissionPolicy):
        def can_view(self, actor, resource):
            return actor.is_active
"""

from __future__ import annotations

import abc
from typing import Any


class BasePermissionPolicy(abc.ABC):
    """
    Abstract base class for all permission policies.

    Each domain feature should subclass this and implement the relevant
    ``can_*`` verbs it exposes.  Unimplemented verbs default to denied.

    Attributes:
        actor: The principal requesting the action (typically a User instance).
        resource: The target domain object (may be None for collection-level checks).
    """

    def __init__(self, actor: Any, resource: Any = None) -> None:
        self.actor = actor
        self.resource = resource

    def can_view(self) -> bool:
        """Return True if the actor may read the resource."""
        return False

    def can_create(self) -> bool:
        """Return True if the actor may create new instances of the resource type."""
        return False

    def can_update(self) -> bool:
        """Return True if the actor may modify the resource."""
        return False

    def can_delete(self) -> bool:
        """Return True if the actor may delete the resource."""
        return False

    def can_export(self) -> bool:
        """Return True if the actor may export resource data."""
        return False

    @abc.abstractmethod
    def has_permission(self, action: str) -> bool:
        """
        Evaluate a named permission action against the actor and resource.

        Args:
            action: A string naming the action (e.g. "view", "delete").

        Returns:
            True if the action is permitted, False otherwise.
        """

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"actor={getattr(self.actor, 'pk', self.actor)!r}, "
            f"resource={type(self.resource).__name__ if self.resource else None!r})"
        )


class AllowAllPolicy(BasePermissionPolicy):
    """Permissive policy used in tests and public endpoints."""

    def has_permission(self, action: str) -> bool:  # noqa: ARG002
        return True

    def can_view(self) -> bool:
        return True

    def can_create(self) -> bool:
        return True

    def can_update(self) -> bool:
        return True

    def can_delete(self) -> bool:
        return True


class DenyAllPolicy(BasePermissionPolicy):
    """Restrictive policy used as a safe default."""

    def has_permission(self, action: str) -> bool:  # noqa: ARG002
        return False


__all__ = [
    "BasePermissionPolicy",
    "AllowAllPolicy",
    "DenyAllPolicy",
]
