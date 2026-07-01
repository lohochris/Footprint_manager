"""
Prompt template management for Footprint Manager AI module.

Provides ``PromptTemplate`` — a structured dataclass for managing LLM
prompt templates with variable interpolation.  Templates are versioned and
stored in this module; the prompt registry maps names to active templates.

Usage::

    from apps.ai.prompts import PromptTemplate, registry

    template = registry.get("investigation_summary")
    rendered = template.render({"title": "ACME Corp Breach", "findings": "..."})
"""

from __future__ import annotations

from dataclasses import dataclass, field
from string import Template


@dataclass(frozen=True)
class PromptTemplate:
    """
    Versioned LLM prompt template.

    Uses Python's ``string.Template`` substitution syntax (``$variable``
    or ``${variable}``).

    Attributes:
        name: Unique template identifier.
        system: System prompt text (may contain variables).
        user: User-turn prompt text (may contain variables).
        description: Human-readable description of the template's purpose.
        version: Schema version for tracking prompt evolution.
        tags: Categorisation tags for retrieval and auditing.
    """

    name: str
    system: str
    user: str
    description: str = ""
    version: int = 1
    tags: list[str] = field(default_factory=list)

    def render(self, variables: dict[str, str]) -> tuple[str, str]:
        """
        Render the system and user prompts with *variables*.

        Args:
            variables: Mapping of variable names to their values.

        Returns:
            Tuple of ``(rendered_system, rendered_user)`` strings.
        """
        rendered_system = Template(self.system).safe_substitute(variables)
        rendered_user = Template(self.user).safe_substitute(variables)
        return rendered_system, rendered_user


class PromptRegistry:
    """In-memory registry mapping template names to ``PromptTemplate`` instances."""

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = {}

    def register(self, template: PromptTemplate) -> None:
        """Register *template* under its ``name``."""
        self._templates[template.name] = template

    def get(self, name: str) -> PromptTemplate:
        """
        Retrieve a template by *name*.

        Raises:
            KeyError: If no template with *name* is registered.
        """
        if name not in self._templates:
            raise KeyError(f"No prompt template registered under {name!r}.")
        return self._templates[name]

    def all(self) -> list[PromptTemplate]:
        """Return all registered templates."""
        return list(self._templates.values())

    def names(self) -> list[str]:
        """Return all registered template names."""
        return list(self._templates.keys())


#: Global prompt registry — populated during app initialisation.
registry: PromptRegistry = PromptRegistry()

__all__ = [
    "PromptTemplate",
    "PromptRegistry",
    "registry",
]
