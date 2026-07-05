import uuid
from typing import List, Dict, Any

class CorrelationEngine:
    @staticmethod
    def build_trace_tree(tenant_id: uuid.UUID, trace_id: str) -> Dict[str, Any]:
        """
        Builds a hierarchical tree of a trace.
        """
        from ..selectors import TraceSelector
        traces = TraceSelector.get_trace_tree(tenant_id, trace_id)

        span_map = {t.span_id: t for t in traces}
        tree = []

        for trace in traces:
            if trace.parent_span_id and trace.parent_span_id in span_map:
                # Add to parent
                parent = span_map[trace.parent_span_id]
                if not hasattr(parent, "children"):
                    parent.children = []  # type: ignore[attr-defined]
                parent.children.append(trace)  # type: ignore[attr-defined]
            else:
                # Root node
                tree.append(trace)

        # Normally would format as dicts, but for Sprint 15 we just return the raw traces
        # The ViewSet/Serializer will handle serialization.
        return {"tree": tree}
