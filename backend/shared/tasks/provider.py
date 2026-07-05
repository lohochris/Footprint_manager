import abc
import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Dict, Optional
from uuid import UUID


@dataclass
class TaskContext:
    """Typed context for background execution to ensure authorization and isolation."""
    task_id: UUID
    tenant_id: UUID
    organization_id: UUID
    user_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "task_id": str(self.task_id),
            "tenant_id": str(self.tenant_id),
            "organization_id": str(self.organization_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "metadata": self.metadata or {},
        }


class BaseTaskProvider(abc.ABC):
    """Abstract provider for executing long-running background tasks."""

    @abc.abstractmethod
    def enqueue(self, context: TaskContext, func: Callable, *args, **kwargs) -> str:
        """Enqueue a task for execution. Returns the external job ID."""
        pass


class InProcessTaskProvider(BaseTaskProvider):
    """Simple in-process asyncio task provider for development/testing."""

    def enqueue(self, context: TaskContext, func: Callable, *args, **kwargs) -> str:
        # Note: This is an overly simple implementation intended as a placeholder
        # until a real task queue (like Celery/RabbitMQ) is implemented.
        async def wrap() -> None:
            if asyncio.iscoroutinefunction(func):
                await func(context, *args, **kwargs)
            else:
                # Run synchronous function in an executor thread
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: func(context, *args, **kwargs))

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(wrap())
        except RuntimeError:
            # If no event loop is running, just run it synchronously as a fallback
            if asyncio.iscoroutinefunction(func):
                asyncio.run(wrap())
            else:
                func(context, *args, **kwargs)

        return str(context.task_id)
