import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.subproject import Subproject
from tik_manager4.objects.commons import Commons

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
        self.type = "project"

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
        self.structure_file = os.path.join(self._database_path, "project_structure.json")
        self.set_sub_tree(self._currentValue)
        self._guard.set_project_root(self._absolute_path)
        self._guard.set_database_root(self._database_path)

    def delete_sub_project(self, uid=None, path=None):
        # TODO This requires tests
        # TODO Consider deleting the work folders ??!!?? OR
        # TODO maybe check for publishes? if there is any abort immediately?
        # if user_object.permission_level < 3:
        #     return -1, log.warning("User %s does not have delete permissions" % user_object.get())
        # if not user_object.is_authenticated:
        #     return -1, log.warning("User is not authenticated")
        # state = self._check_permissions(level=2)
        # if state != 1:
        #     return -1

        if uid:
            _remove_path = self.get_path_by_uid(uid)
        else:
            _remove_path = path

        if self._remove_sub_project(uid, path) == -1:
            return -1
        self.apply_settings()
        self._delete_folders(os.path.join(self._database_path, _remove_path))
        return 1

    def create_sub_project(self, name, parent_uid=None, parent_path=None, resolution=None, fps=None):
        """
             Similar to add_sub_project method but creates it under specified parent sub and writes data to
        persistent database

        Args:
            name: (String) Name of the sub-project
            parent_uid: (Int) Parent Sub-Project Unique ID (or project itself.
                                Either this or parent_path needs to be defined
            parent_path: (String) Parent Sub-Project Relative path. If uid defined this will be skipped
            resolution: (Tuple) If not defined, parent resolution will be inherited
            fps: (int) If not defined parent fps will be inherited

        Returns:
            <class Subproject>
        """
        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)

        new_sub = parent_sub.add_sub_project(name, resolution=resolution, fps=fps, uid=None)
        if new_sub == -1:
            return -1
        self.save_structure()
        # self.apply_settings()
        self.create_folders(self._database_path)
        return new_sub

    def create_category(self, name, parent_uid=None, parent_path=None):
        """
        Creates a category AND creates folders and stores it in persistent database

        Args:
            name: (String) Name of the category
            parent_uid: (Int) Parent Sub-Project Unique ID (or project itself.
                                Either this or parent_path needs to be defined
            parent_path: (String) Parent Sub-Project Relative path. If uid defined this will be skipped

        Returns:
            <class Category>
        """

        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)

        new_category = parent_sub.add_category(name)
        if new_category == -1:
            return -1

        self.apply_settings()
        self.create_folders(self._database_path)
        return new_category

    def create_basescene(self, name, category, parent_uid=None, parent_path=None):
        if not parent_uid and not parent_path:
            log.error("Requires at least a parent uid or parent path ")
            return -1
        state = self._check_permissions(level=1)
        if state != 1:
            return -1
        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)
        # confirm category exists
        category_object = parent_sub.get_category(category)
        if category_object == -1:
            log.error("Category %s does not exist" % category)
            return -1

        return category_object.add_base_scene(name)

    def __validate_and_get_sub(self, parent_uid, parent_path):
        """
        Confirms either parent_uid or parent_path provided (other than none) and returns
        the parent subproject class
        Args:
            parent_uid: Unique id of the parent subproject
            parent_path: Relative path of the parent subproject

        Returns: <subproject class>

        """
        # TODO requires test
        if not parent_uid and parent_path == None:
            raise Exception("Requires at least a parent uid or parent path ")
        if parent_uid != None:
            parent = self.find_sub_by_id(parent_uid)
        else:
            parent = self.find_sub_by_path(parent_path)
        if parent == -1:
            raise Exception("Parent cannot identified")
        return parent
