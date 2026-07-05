# Timeline app permissions

class TimelinePermissions:
    VIEW_TIMELINE = "timeline.view"
    MANAGE_TIMELINE = "timeline.manage"
    REPLAY_TIMELINE = "timeline.replay"
    EXPORT_TIMELINE = "timeline.export"

    @classmethod
    def get_all(cls):
        return [
            cls.VIEW_TIMELINE,
            cls.MANAGE_TIMELINE,
            cls.REPLAY_TIMELINE,
            cls.EXPORT_TIMELINE,
        ]
