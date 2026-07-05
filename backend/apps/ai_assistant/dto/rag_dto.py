from dataclasses import dataclass

@dataclass
class RAGSourceDTO:
    """Represents a discrete piece of contextual information for the LLM."""
    source_type: str  # e.g., "evidence", "graph_node", "osint_identifier"
    source_id: str
    content: str
    relevance_score: float = 1.0

@dataclass
class RAGContextDTO:
    """A collection of relevant context to inject into a prompt."""
    query: str
    sources: list[RAGSourceDTO]

    @property
    def formatted_text(self) -> str:
        """Formats the context into a string suitable for injection into a prompt."""
        if not self.sources:
            return "No additional context found."

        formatted = "Available Context Data:\n"
        for s in self.sources:
            formatted += f"[{s.source_type}:{s.source_id}] {s.content}\n"
        return formatted
