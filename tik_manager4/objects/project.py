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
        # tik_database = self._io.folder_check(os.path.join(self._path, "tikDatabase"))
        # self.settings_file = os.path.join(tik_database, "project_structure.json")

        sm_database = self._io.folder_check(os.path.join(self._path, "smDatabase"))
        self.settings_file = os.path.join(sm_database, "projectSettings.json")

        if not self.get_property("fps"):
            self.add_property("fps", 25)
        if not self.get_property("resolution"):

        if "fps" not in self.all_properties:
            self.add_property("fps", 25)
        if "Resolution" not in self.all_properties:
            self.add_property("Resolution", [1920, 1080])
        self._fps = self._currentValue["FPS"]
        self._resolution = self._currentValue["Resolution"]
        return


