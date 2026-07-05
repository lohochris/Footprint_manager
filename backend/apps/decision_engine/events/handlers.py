import logging

from backend.apps.decision_engine.dto import EvaluationInputDTO
from backend.apps.decision_engine.services import DecisionService
from backend.shared.event_bus import EventHandler
from backend.shared.events import BaseDomainEvent

logger = logging.getLogger(__name__)


class DecisionEngineEventHandler(EventHandler[BaseDomainEvent]):
    """
    Generic handler that intercepts relevant domain events and feeds them
    into the Decision Engine for policy evaluation.
    """

    def __init__(self, decision_service: DecisionService | None = None):
        self.decision_service = decision_service or DecisionService()

    def handle(self, event: BaseDomainEvent) -> None:
        tenant_id = event.metadata.get("tenant_id")
        if not tenant_id:
            logger.warning(f"Discarding event {event.event_id} due to missing tenant_id in metadata")
            return

        input_dto = EvaluationInputDTO(
            tenant_id=tenant_id,
            event_type=event.__class__.event_type,
            payload=event.to_dict(),
            trace_identifier=event.metadata.get("correlation_id", str(event.event_id)),
        )

        try:
            self.decision_service.process_event(input_dto)
        except Exception as e:
            logger.exception(f"Failed to process event {event.event_id} through Decision Engine: {e}")
            # Note: We catch and log here to ensure event bus continues if one context fails,
            # but usually the event bus itself handles isolated failures. Re-raising lets the bus know it failed.
            raise
