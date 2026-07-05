from backend.apps.ai_assistant.models import PromptTemplate
from backend.apps.ai_assistant.dto.rag_dto import RAGContextDTO
import logging

logger = logging.getLogger(__name__)

class PromptService:
    """Assembles prompts dynamically from DB templates and RAG context."""

    def assemble(
        self,
        tenant_id: str,
        template_name: str,
        template_version: str,
        rag_context: RAGContextDTO | None = None,
        **kwargs: str,
    ) -> str:
        """Fetch a template and populate it with variables and context."""

        try:
            template = PromptTemplate.objects.get(
                tenant_id=tenant_id,
                name=template_name,
                version=template_version,
                is_active=True
            )
            template_text = template.template_text
        except PromptTemplate.DoesNotExist:
            logger.warning(f"Template {template_name} v{template_version} not found. Using fallback.")
            template_text = self._get_fallback_template(template_name)

        # Inject RAG Context if provided
        if rag_context:
            kwargs["rag_context"] = rag_context.formatted_text
        else:
            kwargs["rag_context"] = ""

        # Safely format the template
        try:
            return template_text.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable for template {template_name}: {e}")
            return template_text

    def _get_fallback_template(self, name: str) -> str:
        if name == "investigation_summary":
            return "Summarize the investigation. Context:\n{rag_context}"
        if name == "default_chat":
            return "You are an AI assistant for Footprint Manager. Answer the query using ONLY the provided context:\n{rag_context}"
        return "System Prompt:\n{rag_context}"
