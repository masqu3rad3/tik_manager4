import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.basescene import BaseScene

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Project(Settings):
    def __init__(self):
        super(Project, self).__init__()
        self._path = None
        self._name = None
        self._resolution = None
        self._fps = None

        self._is_root = True
        self._sub_projects = []
        self._base_scenes = []

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def resolution(self):
        return self._resolution

    @property
    def fps(self):
        return self._fps

    @property
    def sub_projects(self):
        return self._sub_projects

    def create_project(self, path):
        if not os.path.isdir(os.path.normpath(path)):
            os.makedirs(os.path.normpath(path))
        else:
            msg = "Project already exists"
            log.warning(msg)
            return 0

        # create folder structure
        os.makedirs(os.path.join(path, "smDatabase"))
        os.makedirs(os.path.join(path, "scenes"))

        self.file_path = os.path.join(path, "smDatabase", "projectSettings.json")
        # add the default resolution and fps if not set
        if not self._resolution:
            self.add("resolutionX", "1920")
            self.add("resolutionY", "1080")
        if not self._fps:
            self.add("fps", "24")
        self.apply()

    def add_sub_project(self, name):
        self._sub_projects.append(name)
        pass

    def scan_base_scenes(self):
        """Finds the base scenes defined in the database"""
        if not self._path:
            msg = "Project path is not available"
            log.warning(msg)
            return 0
        # TODO WIP
        pass

