# Reporting app permissions

class ReportingPermissions:
    VIEW_REPORT = "report.view"
    CREATE_REPORT = "report.create"
    PUBLISH_REPORT = "report.publish"
    EXPORT_REPORT = "report.export"
    MANAGE_TEMPLATE = "template.manage"

    @classmethod
    def get_all(cls):
        return [
            cls.VIEW_REPORT,
            cls.CREATE_REPORT,
            cls.PUBLISH_REPORT,
            cls.EXPORT_REPORT,
            cls.MANAGE_TEMPLATE,
        ]
