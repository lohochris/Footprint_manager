from backend.shared.event_bus import event_bus

class ReportingEventPublisher:
    @staticmethod
    def publish_report_generated(payload: dict) -> None:
        event_bus.publish("ReportGenerated", payload)

    @staticmethod
    def publish_report_published(payload: dict) -> None:
        event_bus.publish("ReportPublished", payload)

    @staticmethod
    def publish_report_exported(payload: dict) -> None:
        event_bus.publish("ReportExported", payload)

    @staticmethod
    def publish_report_downloaded(payload: dict) -> None:
        event_bus.publish("ReportDownloaded", payload)

__all__ = ["ReportingEventPublisher"]
