import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.subproject import Subproject

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Project(Settings, Subproject):
    def __init__(self, path=None, name=None, resolution=None, fps=None):
        super(Project, self).__init__()
        self._path = path
        self._database_path = None
        self._name = name
        self._resolution = resolution
        self._fps = fps

        # This makes sure the project folder is tik_manager4 ready
        if path:
            self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, val):
        self._path = val
        self._database_path = self._io.folder_check(os.path.join(self._path, "tikDatabase"))
        self.settings_file = os.path.join(self._database_path, "project_structure.json")
        #
        if not self.get_property("path"):
            self.add_property("path", self._path)
        if not self.get_property("fps"):
            self.add_property("fps", 25)
        if not self.get_property("resolution"):
            self.add_property("resolution", [1920, 1080])
        self.apply_settings()
        self.set_sub_tree(self._currentValue)
        return

    @property
    def database_path(self):
        return self._database_path

    def save_structure(self):
        self._currentValue = self.get_sub_tree()
        self.apply_settings()
