from django.apps import AppConfig


class DecisionEngineConfig(AppConfig):
    name = "backend.apps.decision_engine"
    verbose_name = "Decision Engine"

    def ready(self) -> None:
        pass
