import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.subproject import Subproject
# from tik_manager4.objects.user import User
# from tik_manager4.objects.guard import Guard

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Project(Settings, Subproject):
    # _guard = Guard()
    def __init__(self, path=None, name=None, resolution=None, fps=None):
        super(Project, self).__init__()
        self._path = path
        self._database_path = None
        self._name = name
        self._resolution = resolution
        self._fps = fps
        # We define a user object here. This way we can access permission and authentication
        # status using class properties of user object
        # self._user = User()

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
        self.create_folders(root=self.database_path)
        self.create_folders(root=self.absolute_path)
        self.apply_settings()

    def set(self, absolute_path):
        self._absolute_path = absolute_path
        self._relative_path = ""
        self.name = os.path.basename(absolute_path)
        self._database_path = self._io.folder_check(os.path.join(absolute_path, "tikDatabase"))
        self.settings_file = os.path.join(self._database_path, "project_structure.json")
        self.set_sub_tree(self._currentValue)

    def delete_sub_project(self, user_object, uid=None, path=None):
        # TODO This requires tests
        # TODO Consider deleting the work folders ??!!?? OR
        # TODO maybe check for publishes? if there is any abort immediately?
        if user_object.permission_level < 3:
            return -1, log.warning("User %s does not have delete permissions" % user_object.get())
        if not user_object.is_authenticated:
            return -1, log.warning("User is not authenticated")
        self._remove_sub_project(uid, path)
        self.apply_settings()
        self._delete_folders(os.path.join(self._database_path, path))

    # def testing(self):
    #     print(self._guard.permission_level)
    #     print(self._guard.is_authenticated)
    #     return(self._guard.permission_level, self._guard.is_authenticated)

