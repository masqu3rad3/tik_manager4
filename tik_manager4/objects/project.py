import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.subproject import Subproject

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Project(Settings, Subproject):
    def __init__(self):
        super(Project, self).__init__()
        self._path = None
        self._name = None
        self._resolution = None
        self._fps = None

        self._base_scenes = []

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, val):
        self._path = val
        sm_database = self._io.folder_check(os.path.join(self._path, "smDatabase"))
        self.settings_file = os.path.join(sm_database, "projectSettings.json")
        if "FPS" not in self.all_properties:
            self.add_property("FPS", 25)
        if "Resolution" not in self.all_properties:
            self.add_property("Resolution", [1920, 1080])
        self._fps = self._currentValue["FPS"]
        self._resolution = self._currentValue["Resolution"]
        return

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    # def get_project_tree(self):
    #     data = {}
    #     subs = self._sub_projects
    #     for sub in self._sub_projects:
    #         data["id"] = sub.id
    #         data["name"] = sub.name
    #         data["path"] = sub.path
    #         data["categories"] = sub.categories
    #         data["subs"] = sub.subs
    #
    #     while subs != []:
    #         for x in subs:
    #             data[x]
    #             yield x.name
    #             subs = x._sub_projects
    #     return data
    #     pass

    def __str__(self):
        return self._name

