import os
from glob import glob
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.subproject import Subproject
from tik_manager4.objects.work import Work
# from tik_manager4.objects.commons import Commons

# log = filelog.Filelog(logname=__name__, filename="tik_manager4")


# class Project(Settings, Subproject):
class Project(Subproject):
    log = filelog.Filelog(logname=__name__, filename="tik_manager4")
    def __init__(self, path=None, name=None, resolution=None, fps=None):
        super(Project, self).__init__()
        self.structure = Settings()
        self.settings = Settings()
        self.metadata_definitions = Settings()
        self._path = path
        self._database_path = None
        self._name = name
        self._resolution = resolution
        self._fps = fps
        self.__mode = ""

        # This makes sure the project folder is tik_manager4 ready
        if path:
            self._set(path)

        # Absolute path do not go into the project_structure.json
        self._absolute_path = ""

    @property
    def absolute_path(self):
        return self._absolute_path

    @property
    def folder(self):
        """Return the root of the project, where all projects lives happily"""
        return os.path.abspath(os.path.join(self._absolute_path, os.pardir))

    @property
    def path(self):
        """This is overriden to return an empty string indicating that this is the project root"""
        return ""  # return empty string instead "\\" for easier path join

    @property
    def database_path(self):
        return self._database_path

    def save_structure(self):
        self.structure._currentValue = self.get_sub_tree()
        self.create_folders(root=self.database_path)
        self.create_folders(root=self.absolute_path)
        self.structure.apply_settings()

    def _set(self, absolute_path):
        self._absolute_path = absolute_path
        self._relative_path = ""
        self.name = os.path.basename(absolute_path)
        self._database_path = self.structure._io.folder_check(os.path.join(absolute_path, "tikDatabase"))
        self.structure.settings_file = os.path.join(self._database_path, "project_structure.json")
        self.set_sub_tree(self.structure.properties)
        self.guard.set_project_root(self._absolute_path)
        self.guard.set_database_root(self._database_path)
        # get project settings
        self.settings.settings_file = os.path.join(self._database_path, "project_settings.json")
        self.settings.set_fallback(self.guard.commons.project_settings.settings_file)
        self.metadata_definitions.settings_file = os.path.join(self._database_path, "project_metadata.json")
        self.metadata_definitions.set_fallback(self.guard.commons.metadata.settings_file)

    def delete_sub_project(self, uid=None, path=None):
        if uid:
            _remove_path = self.get_path_by_uid(uid)
        else:
            _remove_path = path

        if self._remove_sub_project(uid, path) == -1:
            return -1
        self._delete_folders(os.path.join(self._database_path, _remove_path))
        self.save_structure()
        return 1

    def create_sub_project(self, name, parent_uid=None, parent_path=None, **kwargs):
        """
             Similar to add_sub_project method but creates it under specified parent sub and writes data to
        persistent database

        Args:
            name: (String) Name of the subproject
            parent_uid: (Int) Parent Subproject Unique ID or project itself.
                                Either this or parent_path needs to be defined
            parent_path: (String) Parent Sub-Project Relative path. If uid defined this will be skipped

        Returns:
            <class Subproject>
        """
        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)
        if parent_sub == -1:
            return -1

        new_sub = parent_sub.add_sub_project(name, parent_sub=parent_sub, uid=None, **kwargs)
        if new_sub == -1:
            return -1
        self.save_structure()
        self.create_folders(self._database_path)
        return new_sub

    def edit_sub_project(self, uid=None, path=None, name=None, **properties):
        """Edits a subproject and stores it in persistent database"""
        state = self.check_permissions(level=2)
        if state != 1:
            return -1
        sub = self.__validate_and_get_sub(uid, path)
        if sub == -1:
            return -1
        if name:
            sub.name = name

        # get the subproject tree
        kill_list = []
        sub_tree = sub.get_sub_tree()
        for key, value in sub_tree.items():
            if key not in ["name", "id", "path", "subs"]:
                kill_list.append(key)
        for key in kill_list:
            del sub_tree[key]

        # update the sub_tree with properties
        sub_tree.update(properties)

        sub.set_sub_tree(sub_tree)
        # sub.metadata.override(properties)
        self.save_structure()
        return 1

    def create_task(self, name, categories=None, parent_uid=None, parent_path=None):
        """Creates a task and stores it in persistent database"""
        if not parent_uid and not parent_path:
            self.log.error("Requires at least a parent uid or parent path ")
            return -1
        # state = self._check_permissions(level=1)
        # if state != 1:
        #     return -1
        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)
        # confirm category exists
        # category_object = parent_sub.get_category(category)
        # if category_object == -1:
        #     log.error("Category %s does not exist" % category)
        #     return -1
        task = parent_sub.add_task(name, categories=categories)
        if not task:
            return -1  # There is a task with same absolute path
        return task

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
        if not parent_uid and parent_path is None:
            raise Exception("Requires at least a parent uid or parent path ")
        if parent_uid is not None:
            parent = self.find_sub_by_id(parent_uid)
        else:
            parent = self.find_sub_by_path(parent_path)
        if parent == -1:
            self.log.error("Parent subproject does not exist")
        #     raise Exception("Parent cannot identified")
        return parent

    def find_work_by_absolute_path(self, file_path):
        """Using the absolute path of the scene file return work object"""

        parent_path = os.path.dirname(file_path)
        # get the base name without extension
        base_name = os.path.basename(file_path)
        relative_path = os.path.relpath(parent_path, self.absolute_path)
        database_path = self.get_abs_database_path(relative_path)
        # get all the work files under the database path
        work_files = glob(os.path.join(database_path, "*.twork"), recursive=False)
        for work_file in work_files:
            _work = Work(work_file)
            for version in _work.versions:
                if version.get("scene_path") == base_name:
                    return _work

    # def scan_tasks(self):
    #     self._tasks = {}
    #     super(Project, self).scan_tasks()
    #     return self._tasks



