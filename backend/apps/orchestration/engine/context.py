import uuid
from typing import Any, Dict
from dataclasses import dataclass, field

@dataclass
class ExecutionContext:
    """
    Encapsulates the state and parameters for a workflow or step execution.
    """
    workflow_execution_id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID | None = None
    creator_id: int | None = None

    # Global variables accessible across steps
    variables: Dict[str, Any] = field(default_factory=dict)

    # Accumulated outputs from completed steps, keyed by step_id
    step_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Execution trace metadata
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def set_variable(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def add_step_output(self, step_id: str, output: Dict[str, Any]) -> None:
        self.step_outputs[step_id] = output

    def get_step_output(self, step_id: str) -> Dict[str, Any]:
        return self.step_outputs.get(step_id, {})
