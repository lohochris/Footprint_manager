"""Pipeline Registry

Provides a simple global registry for mapping operation identifiers (e.g., "organization.create")
to callable handler functions. Handlers are expected to implement the business logic for a
service operation. The registry is deliberately lightweight to keep the core framework
framework‑agnostic.
"""

from collections.abc import Callable


class PipelineRegistry:
    """Global registry for service operation handlers.

    The registry stores a mapping from a dotted operation name to a callable. The
    callable signature is intentionally un‑typed; concrete services can define
    their own expectations. The registry raises a ``KeyError`` when a handler is
    requested for an unknown operation.
    """

    _handlers: dict[str, Callable] = {}

    @classmethod
    def register(cls, operation: str, handler: Callable) -> None:
        """Register a handler for a given operation.

        Args:
            operation: Dotted operation name, e.g., ``"organization.create"``.
            handler: Callable that performs the business logic.
        """
        cls._handlers[operation] = handler

    @classmethod
    def get_handler(cls, operation: str) -> Callable:
        """Retrieve the handler for *operation*.

        Raises:
            KeyError: If no handler has been registered for the operation.
        """
        try:
            return cls._handlers[operation]
        except KeyError as exc:
            raise KeyError(f"No handler registered for operation '{operation}'") from exc

    @classmethod
    def clear(cls) -> None:
        """Clear all registered handlers (useful for test isolation)."""
        cls._handlers.clear()


# Register WorkspaceService operations
from backend.apps.organizations.services.workspace_service import WorkspaceService  # noqa: E402

PipelineRegistry.register(
    'workspace.create',
    lambda **payload: WorkspaceService.create_workspace(**payload),
)
PipelineRegistry.register(
    'workspace.update',
    lambda **payload: WorkspaceService.update_workspace(**payload),
)
PipelineRegistry.register(
    'workspace.archive',
    lambda **payload: WorkspaceService.archive_workspace(**payload),
)
PipelineRegistry.register(
    'workspace.restore',
    lambda **payload: WorkspaceService.restore_workspace(**payload),
)
PipelineRegistry.register(
    'workspace.delete',
    lambda **payload: (
        WorkspaceService.delete_workspace(**payload)
        if hasattr(WorkspaceService, 'delete_workspace')
        else None
    ),
)
PipelineRegistry.register(
    'workspace.update_settings',
    lambda **payload: WorkspaceService.update_workspace_settings(**payload),
)
PipelineRegistry.register(
    'workspace.change_visibility',
    lambda **payload: WorkspaceService.change_workspace_visibility(**payload),
)
PipelineRegistry.register(
    'workspace.change_status',
    lambda **payload: WorkspaceService.change_workspace_status(**payload),
)
