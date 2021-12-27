import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.subproject import Subproject

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Project(Settings, Subproject):
    def __init__(self):
        super(Project, self).__init__()
        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, val):
        self._path = val
        tik_database = self._io.folder_check(os.path.join(self._path, "tikDatabase"))
        self.settings_file = os.path.join(tik_database, "project_structure.json")
        #
        # sm_database = self._io.folder_check(os.path.join(self._path, "smDatabase"))
        # self.settings_file = os.path.join(sm_database, "projectSettings.json")
        if not self.get_property("path"):
            self.add_property("path", self._path)
        if not self.get_property("fps"):
            self.add_property("fps", 25)
        if not self.get_property("resolution"):
            self.add_property("resolution", [1920, 1080])
        # self.fps = self._currentValue["fps"]
        # self.resolution = self._currentValue["resolution"]
        self.apply_settings()
        print("**************")
        print(self._currentValue)
        self.set_sub_tree(self._currentValue)
        #
        # if "fps" not in self.all_properties:
        #     self.add_property("fps", 25)
        # if "resolution" not in self.all_properties:
        #     self.add_property("resolution", [1920, 1080])
        return

    def save_structure(self):
        self._currentValue = self.get_sub_tree()
        self.apply_settings()
