from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity

class Work(Settings, Entity):
    def __init__(self, name=None,
                 path=None):
        super(Work, self).__init__()

        self._relative_path = self.get_property("path") or path
        # self._note = note
        # self._thumbnail = thumbnail
        # self._preview = preview or {}
        # self._ranges = ranges

