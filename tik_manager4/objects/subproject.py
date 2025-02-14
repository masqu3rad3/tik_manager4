90# pylint: disable=super-with-arguments
"""Module for Subproject object."""

from pathlib import Path
import shutil

from fnmatch import fnmatch

from tik_manager4.core.constants import ObjectType
import tik_manager4.objects.task
from tik_manager4.core import filelog
from tik_manager4.objects.metadata import Metadata
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.task import Task

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Subproject(Entity):
    """Subproject object to hold subproject data and hierarchy.

    Subproject objects doesn't have any settings file. They are
    populated by the project object using the project_structure.json.
    """
    object_type = ObjectType.SUBPROJECT

    def __init__(self, parent_sub=None, metadata=None, **kwargs):
        """Initialize Subproject object.
        Args:
            parent_sub (Subproject): The parent subproject.
            metadata (Metadata): Metadata object to hold any extra data.
            **kwargs: Arbitrary keyword arguments.
        """
        super(Subproject, self).__init__(**kwargs)
        self.__parent_sub = parent_sub
        self._sub_projects: dict = {}
        self._tasks: dict = {}
        self._metadata = metadata or Metadata({})

    @property
    def parent(self):
        """The Parent subproject."""
        return self.__parent_sub

    @property
    def subs(self):
        """All subprojects as dictionary."""
        return self._sub_projects

    @property
    def tasks(self):
        """Return all NON-DELETED tasks under the subproject as dictionary where each key
        is the name of the task and value is a task object."""
        # filter the tasks that are not deleted
        return {task_name: task_obj
         for task_name, task_obj
         in self._tasks.items() if not task_obj.deleted}

    @property
    def all_tasks(self):
        """All tasks, including the deleted ones under the subproject."""
        return self._tasks

    @property
    def metadata(self):
        """The metadata associated with the subproject."""
        return self._metadata

    @property
    def deleted(self):
        """Whether the subproject is deleted or not."""
        return self.metadata.get_value("deleted", fallback_value=False)

    @property
    def parent_sub(self):
        """The parent subproject."""
        return self.__parent_sub

    @property
    def type(self):
        """The type of the subproject."""
        return self.metadata.get_value("mode", fallback_value="global")

    def get_project(self):
        """The project object."""
        # traverse up until the project is found
        return self.__parent_sub.get_project()

    def revive(self):
        """Revive the subproject if it is deleted.
        This is a soft recover. DATABASE IS NOT TOUCHED.
        """
        self.metadata.add_item("deleted", False, overridden=True)
        return 1

    def resurrect(self):
        """Resurrect the subproject if it is deleted."""
        # traverse up until the project, making sure all the parents are revived
        self.revive()
        if self.object_type == ObjectType.PROJECT:
            self.get_project().save_structure() # this is just not to IDE to complain
            return True, "success"
        self.__parent_sub.resurrect()
        return True, "success"

    def replace_metadata(self, metadata):
        """Replace the metadata with the given one."""
        self._metadata = metadata

    def get_sub_tree(self):
        """Return the subproject tree as a dictionary."""
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            # "deleted": self.deleted,
            "subs": [],  # this will be filled with the while loop
        }

        for key, metaitem in self.metadata.items():
            if metaitem.overridden:
                all_data[key] = metaitem.value

        # add the initial dictionary and self into the queue
        # Each queue item is a list.
        # first element is the dictionary point and second is the subproject object
        queue.append([all_data, self])

        while queue:
            current = queue.pop(0)
            parent = current[0]
            sub = current[1]

            for neighbour in list(sub.subs.values()):
                if neighbour not in visited:
                    sub_data = {
                        "id": neighbour.id,
                        "name": neighbour.name,
                        "path": neighbour.path,
                        "subs": [],  # this will be filled with the while loop
                    }
                    # add the deleted flag only if there is a key for it.
                    for key, metaitem in neighbour.metadata.items():
                        if metaitem.overridden:
                            sub_data[key] = metaitem.value

                    parent["subs"].append(sub_data)
                    visited.append(neighbour)
                    queue.append([sub_data, neighbour])

        return all_data

    def set_sub_tree(self, data):
        """Create the subproject from the data dictionary.

        This is for building back the hierarchy from json data.

        Args:
            data (dict): The dictionary data to build the subproject.
        """
        # first clear the subprojects
        self._sub_projects = {}
        persistent_keys = ["id", "name", "path", "subs"]
        visited = []
        queue = []
        self.id = data.get("id", None)
        self._name = data.get("name", None)
        self._relative_path = data.get("path", None)

        # get all remaining keys as metadata
        # inherit parents metadata
        if self.__parent_sub:
            self._metadata = Metadata(
                dict(self.__parent_sub.metadata.get_all_items())
            ) or Metadata({})

        for key, value in data.items():
            if key not in persistent_keys:
                self._metadata.add_item(key, value, overridden=True)

        # append the subproject object and pointer for json as a queue element
        queue.append([self, data.get("subs", [])])

        while queue:
            current = queue.pop(0)
            sub = current[0]
            data_position = current[1]

            for neighbour in data_position:
                if neighbour not in visited:
                    _deleted = neighbour.get("deleted", False)
                    # if _deleted:
                    #     print(f"Skipping {neighbour.get('name')} as it is deleted")
                    #     continue
                    _id = neighbour.get("id", None)
                    _name = neighbour.get("name", None)
                    _relative_path = neighbour.get("path", None)

                    # TODO take a look at this if it can be improved
                    _metadata = Metadata(
                        dict(sub.metadata.get_all_items())
                    ) or Metadata({})
                    properties = {}
                    for key, value in neighbour.items():
                        if key not in persistent_keys:
                            properties[key] = value

                    _metadata.override(properties)
                    sub_project = sub.__build_sub_project(_name, sub, _metadata, _id)

                    # define the path and categories separately
                    sub_project._relative_path = _relative_path

                    # add and override metadata
                    for key, metaitem in sub_project.metadata.items():
                        if neighbour.get(key, None):
                            sub_project.metadata[key].overridden = True

                    visited.append(neighbour)
                    queue.append([sub_project, neighbour.get("subs", [])])

    def __build_sub_project(self, name, parent_sub, metadata, uid):
        """Build a nested subproject.

        Args:
            name (str): Name of the subproject.
            parent_sub (Subproject): Parent subproject object.
            metadata (Metadata): Metadata object to hold any extra data.
            uid (int): Unique id of the subproject.

        Returns:
            Subproject: The created subproject object.
        """

        sub_pr = Subproject(
            name=name, parent_sub=parent_sub, metadata=metadata, uid=uid
        )
        sub_pr.path = str(Path(self.path, name))
        self._sub_projects[name] = sub_pr
        return sub_pr

    def add_sub_project(self, name, parent_sub=None, uid=None, **properties):
        """Add a subproject.

        Requires permissions. Does NOT create folders or store in
        the persistent database.
        Either parent_sub or uid is required.

        Args:
            name (str): Name of the subproject.
            parent_sub (Subproject, optional): Parent subproject object.
            uid (int, optional): Unique id of the subproject.
            deleted (bool, optional): Whether the subproject is deleted or not.
                                        Default is False.
            **properties (dict): Any extra properties to be added to the subproject.

        Returns:
            Subproject or int: The created subproject object if successful,
                -1 otherwise.
        """

        state = self.check_permissions(level=2)
        if state != 1:
            return -1

        # TODO look at this if it can be improved
        _metadata = Metadata(dict(self.metadata.get_all_items())) or Metadata({})
        # eliminate the None values
        properties = {k: v for k, v in properties.items() if v is not None}
        _metadata.override(properties)

        if name in self._sub_projects:
            # check if it is deleted
            if self._sub_projects[name].deleted:
                self._sub_projects[name].revive()
                # set the metadata
                self._sub_projects[name].replace_metadata(_metadata)
                return self._sub_projects[name]

            LOG.warning(
                "{0} already exist in sub-projects of {1}".format(name, self._name)
            )
            return -1

        new_sub = self.__build_sub_project(
            name, parent_sub, _metadata, uid
        )  # keep uid at the end

        return new_sub

    def scan_tasks(self):
        """Scan the subproject for tasks.

        Returns:
            dict: The tasks under the subproject.
        """
        _tasks_search_dir = Path(self.get_abs_database_path())
        _task_paths = list(_tasks_search_dir.glob("*.ttask"))

        # add the file if it is new. if it is not new,
        # check the modified time and update if necessary
        for _task_path in _task_paths:
            _task_name = _task_path.stem
            existing_task = self._tasks.get(_task_name, None)
            if not existing_task:
                _task = Task(absolute_path=_task_path, parent_sub=self)
                self._tasks[_task_name] = _task
            else:
                if existing_task.is_modified():
                    existing_task.refresh()

        # if the lengths are not matching that means some tasks are deleted
        if len(_task_paths) != len(self._tasks):
            # get the task names
            _task_names = [_task_path.stem for _task_path in _task_paths]
            # get the task names that are not in the _task_names
            _deleted_task_names = [
                task_name
                for task_name in self._tasks.keys()
                if task_name not in _task_names
            ]
            # delete the tasks
            for _deleted_task_name in _deleted_task_names:
                del self._tasks[_deleted_task_name]

        return self._tasks

    def add_task(self,
                 name,
                 categories,
                 task_type=None,
                 metadata_overrides=None,
                 uid=None
                 ):
        """
        Add a task to the subproject.

        Args:
            name (str): Name of the task.
            categories (list): List of categories.
            task_type (str, optional): Type of the task. If not given,
                it is inherited from the parent subproject (mode).
            metadata_overrides (dict, optional): Metadata overrides for the task.
            uid (int, optional): Unique id of the task.

        Returns:
            Task or int: The created task object if successful, -1 otherwise.

        """
        # pylint: disable=too-many-arguments

        metadata_overrides = metadata_overrides or {}

        # inherit the task type from the parent subproject 'mode' if not specified
        task_type = task_type or self.metadata.get_value("mode", None)
        file_name = f"{name}.ttask"
        relative_path = Path(self.path, file_name)
        abs_path = Path(self.guard.database_root, relative_path)
        if abs_path.exists():
            # instanciate the task object and see if its deleted or not
            _task = Task(absolute_path=abs_path, parent_sub=self)
            if not _task.deleted:
                LOG.warning(
                    f"There is a task under this sub-project with the same name => {name}"
                )
                return -1
            # edit the task
            _task.revive()
            _task.edit(categories=categories, metadata_overrides=metadata_overrides)
            self._tasks[name] = _task
            return _task

        _task_id = uid or self.generate_id()
        _task = Task(
            str(abs_path),
            name=name,
            categories=categories,
            path=self.path,
            file_name=file_name,
            parent_sub=self,
            task_id=_task_id,
            metadata_overrides=metadata_overrides,
        )
        _task.add_property("name", name)
        _task.add_property("nice_name", name)
        _task.add_property("creator", self.guard.user)
        _task.add_property("task_id", _task_id)
        _task.add_property("subproject_id", self.id)
        _task.add_property("categories", categories)
        _task.add_property("path", self.path)
        _task.add_property("file_name", file_name)
        _task.add_property("metadata_overrides", metadata_overrides)
        _task.add_property("state", "active")
        if abs_path.exists() and not _task.deleted:
            LOG.warning(
                f"There is a task under this sub-project with the same name => {name}"
            )
            return -1

        _task.apply_settings()
        self._tasks[name] = _task
        return _task

    @staticmethod
    def is_task_empty(task):
        """Check all categories and return True if all are empty.

        Args:
            task (Task): The task object to check.
        """
        return task.is_empty()

    def delete_task(self, task_name):
        """Delete the task from the subproject.

        Args:
            task_name (str): Name of the task to delete.

        Returns:
            tuple: (state(int), message(str)): 1 if the operation is
                successful, -1 otherwise. A message is returned as well.
        """
        # first get the task
        task: tik_manager4.objects.task.Task = self._tasks.get(task_name)
        if not task:
            msg = f"There is no task with the name: {task_name}"
            LOG.warning(msg)
            return False, msg

        # check all categories are empty
        is_empty = task.is_empty()
        permission_level = 2 if is_empty else 3
        state = self.check_permissions(level=permission_level)
        if state != 1:
            return False, "This user doesn't have permissions for this process."

        if not is_empty:
            LOG.warning(
                f"Sending task {task_name} " f"and everything underneath to purgatory."
            )
        task.destroy()

        return True, "success"

    def find_tasks_by_wildcard(self, wildcard):
        """Return the tasks matching the wildcard.

        Search recursively for all subprojects and the tasks inside them.

        Args:
            wildcard (str): The wildcard to match.

        Returns:
            list: List of tasks matching the wildcard.
        """
        _tasks = self.get_tasks_by_wildcard(wildcard)
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            queue.extend(list(current.subs.values()))
            _tasks.extend(current.get_tasks_by_wildcard(wildcard))
        return _tasks

    def find_task_by_id(self, uid):
        """Find the task by id.

        Args:
            uid (int): Unique id of the task.

        Returns:
            Task or int: The task object if successful, -1 otherwise.
        """
        # first check if the task is under this subproject
        _search = self.get_task_by_id(uid)
        if _search != -1:
            return _search
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            queue.extend(list(current.subs.values()))
            _search = current.get_task_by_id(uid)
            if _search != -1:
                return _search
        return -1

    def find_sub_by_id(self, uid):
        """Find the subproject by id.

        Args:
            uid (int): Unique id of the subproject.

        Returns:
            Subproject or int: The subproject object if successful,
                -1 otherwise.
        """
        if self.id == uid:
            return self
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.id == uid:
                return current
            queue.extend(list(current.subs.values()))
        return -1

    def find_sub_by_path(self, path):
        """Find the subproject by path.

        Args:
            path (str): The path of the subproject.

        Returns:
            Subproject or int: The subproject object if successful,
                -1 otherwise.
        """
        if path in ("", "."):  # this is root
            return self
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.path == path:
                return current
            queue.extend(list(current.subs.values()))
        return -1

    def find_subs_by_wildcard(self, wildcard):
        """Find the subproject by wildcard.

        Args:
            wildcard (str): The wildcard to match.

        Returns:
            list: List of subprojects matching the wildcard.
        """
        subs = []
        queue = list(self.subs.values())
        visited = []
        while queue:
            current = queue.pop(0)
            if fnmatch(current.name, wildcard):
                subs.append(current)
            if current not in visited:
                queue.extend(list(current.subs.values()))
        return subs

    def get_uid_by_path(self, path):
        """Get the uid of the subproject by path.

        Args:
            path (str): The path of the subproject.

        Returns:
            int: The unique id of the subproject.
        """
        sub = self.find_sub_by_path(path)
        return sub.id if sub != -1 else sub

    def get_path_by_uid(self, uid):
        """Get the path of the subproject by uid.

        Args:
            uid (int): Unique id of the subproject.

        Returns:
            str: The path of the subproject.
        """
        sub = self.find_sub_by_id(uid)
        return sub.path if sub != -1 else sub

    def get_task_by_id(self, uid):
        """Get the task by id.

        Search through only the tasks under this subproject.

        Args:
            uid (int): Unique id of the task.

        Returns:
            Task or int: The task object if successful, -1 otherwise.
        """
        self.scan_tasks()
        for _task_name, task_object in self.tasks.items():
            if task_object.id == uid:
                return task_object
        return -1

    def get_tasks_by_wildcard(self, name):
        """Get the task by name.

        Search through only the tasks under this subproject.

        Args:
            name (str): The wildcard to match.

        Returns:
            list: List of tasks that match the wildcard.
        """
        self.scan_tasks()
        tasks = []
        for _task_name, task_object in self.tasks.items():
            if fnmatch(_task_name, name):
                tasks.append(task_object)
        return tasks

    @staticmethod
    def is_subproject_empty(sub):
        """Check if the subproject has other subprojects or tasks.

        Args:
            sub (Subproject): The subproject object to check.

        Returns:
            bool: True if the subproject has no other subs or tasks,
                False otherwise.
        """
        sub.scan_tasks()
        return not sub.subs and not sub.tasks

    def is_empty(self):
        """Check if the subproject is empty."""
        self.scan_tasks()
        return not self.subs and not self.tasks

    def destroy(self):
        """Destroy the subproject object.

        This will tag the subproject and all its children as deleted.
        The subproject will not be removed from the database as it is getting
        controlled with the project object.
        """

        # If the subproject is PROJECT, this is not allowed
        if self.object_type == ObjectType.PROJECT:
            LOG.warning("Project Root cannot be deleted.")
            return -1

        state = self.check_permissions(level=2)
        if state != 1:
            return -1

        # if the subproject is not empty, we need to have level 3
        if not self.is_empty():
            state = self.check_permissions(level=3)
            if state != 1:
                return -1

        self.metadata.add_item("deleted", True, overridden=True)

        for task in self.tasks.values():
            result = task.destroy()
            if result != 1:
                return -1

        for sub in self.subs.values():
            result = sub.destroy()
            if result != 1:
                return -1

        return 1

    def _delete_folders(self, root, sub=None):
        """Delete the folders of the subproject starting from the given root.

        Args:
            root (str): The root path.
            sub (Subproject, optional): The subproject object. If not given the
                current subproject is used.
        """
        sub = sub or self
        folder = Path(root, sub.path)
        if folder.exists():
            shutil.rmtree(str(folder))

    def create_folders(self, root, sub=None):
        """Create folders for subprojects and categories below given root path.

        Args:
            root (str): The root path.
            sub (Subproject, optional): The subproject object. If not given the
                current subproject is used.
        """
        sub = sub or self
        folder = Path(root, sub.path)
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        _ = [sub.create_folders(root, sub=sub) for sub in sub.subs.values()]
