from pathlib import Path
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.subproject import Subproject
from tik_manager4.objects.work import Work
from tik_manager4 import dcc
from tik_manager4.objects.publisher import Publisher

class Project(Subproject):
    log = filelog.Filelog(logname=__name__, filename="tik_manager4")

    def __init__(self, path=None, name=None, resolution=None, fps=None):
        super(Project, self).__init__()
        self.publisher = Publisher(self)
        self.structure = Settings()
        self.settings = Settings()
        self.preview_settings = Settings()
        self.category_definitions = Settings()
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
        return str(Path(self._absolute_path).parent)

    @property
    def path(self):
        """Return an empty string indicating the project root."""
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
        self.__init__()
        _absolute_path_obj = Path(absolute_path)

        self._absolute_path = absolute_path
        self._relative_path = ""
        self.name = _absolute_path_obj.name
        _database_path_obj = _absolute_path_obj / "tikDatabase"
        _database_path_obj.mkdir(parents=True, exist_ok=True)
        self._database_path = str(_database_path_obj)
        self.structure.settings_file = str(_database_path_obj / "project_structure.json")
        # self.structure = Settings(file_path=str(_database_path_obj / "project_structure.json"))
        self.set_sub_tree(self.structure.properties)
        self.guard.set_project_root(self.absolute_path)
        self.guard.set_database_root(self.database_path)
        # get project settings
        self.settings.settings_file = str(_database_path_obj / "project_settings.json")
        self.settings.set_fallback(self.guard.commons.project_settings.settings_file)
        self.guard.set_project_settings(self.settings)
        # get preview settings
        self.preview_settings.settings_file = str(_database_path_obj / "preview_settings.json")
        self.preview_settings.set_fallback(self.guard.commons.preview_settings.settings_file)
        self.guard.set_preview_settings(self.preview_settings)

        # get category definitions
        self.category_definitions.settings_file = str(_database_path_obj / "category_definitions.json")
        self.category_definitions.set_fallback(self.guard.commons.category_definitions.settings_file)
        self.guard.set_category_definitions(self.category_definitions)

        self.metadata_definitions.settings_file = str(_database_path_obj / "project_metadata.json")
        self.metadata_definitions.set_fallback(
            self.guard.commons.metadata.settings_file
        )

    def delete_sub_project(self, uid=None, path=None):
        if uid:
            _remove_path = self.get_path_by_uid(uid)
        else:
            _remove_path = path

        if self._remove_sub_project(uid, path) == -1:
            return -1
        self._delete_folders(str(Path(self._database_path, _remove_path)))
        # self._delete_folders(os.path.join(self._database_path, _remove_path))
        self.save_structure()
        return 1

    def create_sub_project(self, name, parent_uid=None, parent_path=None, **kwargs):
        """Create a sub-project under a specified parent sub and write data to
        persistent database.

        Args:
            name: (String) Name of the subproject
            parent_uid: (Int) Parent Subproject Unique ID or project itself.
                                Either this or parent_path needs to be defined
            parent_path: (String) Parent Sub-Project Relative path. If uid defined this
                                will be skipped

        Returns:
            <class Subproject>
        """
        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)
        if parent_sub == -1:
            return -1

        new_sub = parent_sub.add_sub_project(
            name, parent_sub=parent_sub, uid=None, **kwargs
        )
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
        self.save_structure()
        return 1

    def create_task(self, name, categories=None, parent_uid=None, parent_path=None):
        """Creates a task and stores it in persistent database"""
        state = self.check_permissions(level=2)
        if state != 1:
            return -1
        if not parent_uid and not parent_path:
            self.log.error("Requires at least a parent uid or parent path ")
            return -1
        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)
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
        return parent

    def find_work_by_absolute_path(self, file_path):
        """Using the absolute path of the scene file return work object and version number.

        Args:
            file_path: (String) Absolute path of the scene file.

        Returns: Tuple(<work object>, <version number>)
        """

        _file_path_obj = Path(file_path)
        parent_path = _file_path_obj.parent
        # get the base name with extension
        base_name = _file_path_obj.name
        try:
            relative_path = parent_path.relative_to(self.absolute_path)
        except ValueError:
            self.log.error("File path is not under the project root")
            return None, None
        database_path = Path(self.get_abs_database_path(str(relative_path)))
        work_files = database_path.glob("*.twork")
        for work_file in work_files:
            _work = Work(work_file)
            for nmb, version in enumerate(_work.versions):
                if version.get("scene_path") == base_name:
                    return _work, version.get("version_number", nmb)
        return None, None

    def get_current_work(self):
        """Get the current work object AND version by resolving the current scene.

        Returns: Tuple(<work object>, <version number>)
        """
        dcc_handler = dcc.Dcc()
        current_scene_path = dcc_handler.get_scene_file()

        if not current_scene_path:
            return None, None
        return self.find_work_by_absolute_path(current_scene_path)

