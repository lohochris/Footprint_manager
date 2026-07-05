import uuid
from typing import List, Dict, Any
from .dto import TraceDTO
from ..engine.correlation import CorrelationEngine

class TraceService:
    @staticmethod
    def get_trace_tree(tenant_id: uuid.UUID, trace_id: str) -> Dict[str, Any]:
        """
        Returns a structured trace tree.
        """
        tree_dict = CorrelationEngine.build_trace_tree(tenant_id, trace_id)

        # Convert ORM instances to DTOs for the response
        # Using a simple recursive approach for the tree
        def _to_dto(node):
            dto = TraceDTO(
                id=node.id,
                trace_id=node.trace_id,
                span_id=node.span_id,
                parent_span_id=node.parent_span_id,
                name=node.name,
                duration_ms=node.duration_ms,
                status=node.status
            )
            # Just representing the flat DTO list here instead of fully nested,
            # proper tree serialization goes in the ViewSet/Serializer.
            return dto

        return {"tree": [_to_dto(t) for t in tree_dict["tree"]]}
