import pytest
import uuid
from backend.apps.orchestration.engine.context import ExecutionContext
from backend.apps.orchestration.engine.core import WorkflowEngine
from backend.apps.orchestration.engine.registry import StepRegistry, IStepExecutor
from backend.shared.events import DomainEventBus

class DummyExecutor(IStepExecutor):
    def execute(self, step_config: dict, context: ExecutionContext) -> dict:
        return {"dummy": True}

@pytest.fixture(autouse=True)
def setup_registry():
    StepRegistry.register("dummy", DummyExecutor)

def test_execution_context():
    tenant_id = uuid.uuid4()
    execution_id = uuid.uuid4()

    context = ExecutionContext(workflow_execution_id=execution_id, tenant_id=tenant_id)

    context.set_variable("foo", "bar")
    assert context.get_variable("foo") == "bar"

    context.add_step_output("step_1", {"status": "ok"})
    assert context.get_step_output("step_1") == {"status": "ok"}

def test_workflow_engine_execution():
    tenant_id = uuid.uuid4()
    execution_id = uuid.uuid4()

    context = ExecutionContext(workflow_execution_id=execution_id, tenant_id=tenant_id)

    dag = {
        "steps": [
            {"id": "step_1", "type": "dummy", "config": {}}
        ]
    }

    events_fired = []

    def on_event(execution_id, step_id=None, output=None, error=None):
        events_fired.append(True)

    DomainEventBus.subscribe("workflow.started", on_event)
    DomainEventBus.subscribe("step.completed", on_event)

    engine = WorkflowEngine(context, dag)
    engine.execute()

    # Verify outputs were stored in context
    assert context.get_step_output("step_1") == {"dummy": True}

    # Verify events fired (started + completed)
    assert len(events_fired) >= 2
