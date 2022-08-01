import os
from glob import glob
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity


class Task(Settings, Entity):
    def __init__(self, absolute_path,
                 name=None,
                 category=None,
                 path=None
                 ):
        super(Task, self).__init__()
        self.settings_file = absolute_path

        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self._guard.user
        self._category = self.get_property("category") or category
        # self._dcc = self.get_property("dcc") or self._guard.dcc
        self._versions = []
        self._publishes = []
        self._reference_id = self.get_property("referenceID") or None
        self._relative_path = self.get_property("path") or path

    def scan_versions(self, all_dcc=False):
        """
        Scans the task for all versions.
        Args:
            all_dcc: (bool) If True, scans for all dcc versions

        Returns:

        """
        self._versions.clear()

        # override the all_dcc flag if its standalone
        if self._guard.dcc == "Standalone":
            all_dcc = True

        if not all_dcc:
            _search_dir = self.get_abs_database_path(self._guard.dcc)  # this is DCC specific directory
            _version_paths = glob(os.path.join(_search_dir, '{0}.tver'.format(self.name)))
        else:
            _search_dir = self.get_abs_database_path()
            _version_paths = [y for x in os.walk(_search_dir) for y in glob(os.path.join(x[0], '{0}.tver'.format(self.name)))]
        print(_search_dir)
        print("***")
        print("***")
        print("***")
        print("***")
        print(_version_paths)
        print("***")
        print("***")
        print("***")
        print("***")
        # for b_path in _base_scene_paths:
        #     self._versions.append(Task(b_path))

    def add_version(self):
        pass

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
