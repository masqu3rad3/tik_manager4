from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity


class BaseScene(Settings, Entity):
    def __init__(self, name="", category=""):
        super(BaseScene, self).__init__()

        self._name = name
        self.category = category
        self.creator = self._guard.user
        self.host_machine = None
        self._versions = []
        self._publishes = []

        self.type = "basescene"
