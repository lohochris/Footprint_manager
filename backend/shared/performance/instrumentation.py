import functools
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from uuid import UUID

from backend.shared.event_bus import event_bus


@dataclass
class PerformanceContext:
    """Typed context for performance instrumentation telemetry."""
    tenant_id: UUID
    organization_id: UUID
    operation_name: str
    component: str
    user_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": str(self.tenant_id),
            "organization_id": str(self.organization_id),
            "operation_name": self.operation_name,
            "component": self.component,
            "user_id": str(self.user_id) if self.user_id else None,
            "metadata": self.metadata or {},
        }


def track_performance(context_provider: Callable[..., PerformanceContext]):
    """
    Decorator to track execution time and emit a performance telemetry event.
    `context_provider` is a function that extracts/builds the PerformanceContext from the decorated function's arguments.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                
                # We attempt to extract context and emit safely so telemetry never crashes business logic
                try:
                    context = context_provider(*args, **kwargs)
                    event_bus.publish(
                        "PerformanceMetricRecorded",
                        {
                            "context": context.as_dict(),
                            "metric": "duration_ms",
                            "value": duration_ms,
                        },
                    )
                except Exception as e:
                    # Normally we would log to stdout or a raw logger here
                    pass

        return wrapper

    return decorator
