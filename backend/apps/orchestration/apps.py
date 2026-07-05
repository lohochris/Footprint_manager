from django.apps import AppConfig

class OrchestrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.orchestration"
    label = "orchestration"
    verbose_name = "Orchestration & Workflow"
