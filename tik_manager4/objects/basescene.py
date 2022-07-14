from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity


class BaseScene(Settings, Entity):
    def __init__(self, absolute_path,
                 name=None,
                 category=None,
                 ):
        super(BaseScene, self).__init__()
        self.settings_file = absolute_path


        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self._guard.user
        self._category = self.get_property("category") or category
        self._dcc = self.get_property("dcc") or self._guard.dcc
        self._versions = self.get_property("versions") or []
        self._publishes = self.get_property("publishes") or []
        self._reference_id = self.get_property("referenceID") or None

        # self.name = name
        # self.creator = self._guard.user
        # self.category = category
        # # self.path = self.path
        # self.versions = []
        # self.publishes = []
        # self._reference_id = None


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val
        self.add_property("name", val)

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, val):
        self._creator = val
        self.add_property("creator", val)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, val):
        self._category = val
        self.add_property("category", val)

    # @property
    # def path(self):
    #     return self._path

    # @path.setter
    # def path(self, val):
    #     self._path = val
    #     self.add_property("path", val)

    @property
    def versions(self):
        return self._versions

    @versions.setter
    def versions(self, val):
        self._versions = val
        self.add_property("versions", val)

    @property
    def publishes(self):
        return self._publishes

    @publishes.setter
    def publishes(self, val):
        self._publishes = val
        self.add_property("publishes", val)

    @property
    def reference_id(self):
        return self._reference_id

    @reference_id.setter
    def reference_id(self, val):
        self.reference_id = val
        self.add_property("referenceID", val)

    # def __repr__(self):
    #     return self.name



