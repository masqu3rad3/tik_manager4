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
            self.set(path)

        # Absolute path do not go into the project_structure.json
        self._absolute_path = ""

    @property
    def absolute_path(self):
        return self._absolute_path

    @property
    def path(self):
        """This is overriden to return an empty string indicating that this is the project root"""
        return ""  # return empty string instead "\\" for easier path join

    @property
    def database_path(self):
        return self._database_path

    def save_structure(self):
        self._currentValue = self.get_sub_tree()
        self.apply_settings()

    def set(self, absolute_path):
        self._absolute_path = absolute_path
        self._relative_path = os.path.basename(absolute_path)
        self._database_path = self._io.folder_check(os.path.join(absolute_path, "tikDatabase"))
        self.settings_file = os.path.join(self._database_path, "project_structure.json")
        # TODO instead of checking the properties, create templates under defaults to start with
        # TODO these templates can be copied to the database folder as a base
        if not self.get_property("path"):
            self.add_property("path", self.path)
        if not self.get_property("fps"):
            self.add_property("fps", 25)
        if not self.get_property("resolution"):
            self.add_property("resolution", [1920, 1080])
        self.apply_settings()
        self.set_sub_tree(self._currentValue)

    def delete_sub_project(self, uid=None, path=None):
        # TODO This requires tests
        # TODO This needs to be validated against permissions
        # TODO Consider deleting the work folders ??!!?? OR
        # TODO maybe check for publishes? if there is any abort immediately?
        super(Project, self).delete_sub_project(uid, path)
        self._delete_folders(os.path.join(self._database_path, path))
