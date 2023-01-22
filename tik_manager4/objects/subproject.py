# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

from glob import glob
import os
import shutil

from fnmatch import fnmatch
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.task import Task

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Metaitem(object):
    """Hold the value and overridden status of a property."""
    def __init__(self, value, overridden=False):
        """Initialize Metaitem.
        Args:
            value (any): The value of the property.
            overridden (bool): Whether the value is overridden or not.
        """
        self.value = value
        self.overridden = overridden
class Metadata(dict):
    """Metadata class."""
    def __init__(self, data_dictionary):
        """Initialize Metadata object.
        Args:
            data_dictionary (dict): The dictionary to initialize the metadata with.
        """
        super(Metadata, self).__init__(data_dictionary)

        # create a Metaitem for each key in the data_dictionary
        for key, val in data_dictionary.items():
            self.add_item(key, val)

    def add_item(self, key, value, overridden=False):
        """Add an item to the metadata."""
        self[key] = Metaitem(value, overridden=overridden)
        return self[key]

    def get_all_items(self):
        """Return all items in the metadata."""
        for key, val in self.items():
            yield key, val.value

    def get_value(self, key, fallback_value=None):
        """Get the value of a key."""
        if key in self:
            return self[key].value
        return fallback_value

    def is_overridden(self, key):
        """Check if a key is overridden."""
        if key in self:
            return self[key].overridden
        return False

    def override(self, data_dictionary):
        """Override the metadata with a new dictionary."""
        for key, data in data_dictionary.items():
            self[key] = Metaitem(data, overridden=True)
            # if key in self:
            #     self[key].value = data
            #     self[key].overridden = True
            # else:
            #     self[key] = Metaitem(data, overridden=True)


class Subproject(Entity):
    """Subproject object to hold subproject data and hierarchy."""
    def __init__(self,
                 parent_sub=None,
                 metadata=None,
                 **kwargs):
        """Initialize Subproject object.
        Args:
            parent_sub (Subproject): The parent subproject object.
            metadata (Metadata): Metadata object to hold any extra data.
            **kwargs:
        """
        super(Subproject, self).__init__(**kwargs)
        self.__parent_sub = parent_sub
        self._sub_projects = {}
        self._tasks = {}
        self._metadata = metadata or Metadata({})

    @property
    def parent(self):
        """Return the parent subproject."""
        return self.__parent_sub

    @property
    def subs(self):
        """Return the subprojects."""
        return self._sub_projects

    @property
    def tasks(self):
        """Return the tasks of the subproject."""
        return self._tasks

    # @property
    # def properties(self):
    #     """Return the subproject properties as a dictionary"""
    #     return {
    #         "id": self.id,
    #         "name": self.name,
    #         "path": self.path,
    #     }

    @property
    def metadata(self):
        """Return the metadata."""
        return self._metadata

    def get_sub_tree(self):
        """Return the subproject tree as a dictionary"""
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
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
                    for key, metaitem in neighbour.metadata.items():
                        if metaitem.overridden:
                            sub_data[key] = metaitem.value

                    parent["subs"].append(sub_data)
                    visited.append(neighbour)
                    queue.append([sub_data, neighbour])

        return all_data

    def set_sub_tree(self, data):
        """Create the subproject from the data dictionary.
        This is for building back the hierarchy from json data
        """
        persistent_keys = ["id", "name", "path", "subs"]
        visited = []
        queue = []
        self.id = data.get("id", None)
        self._name = data.get("name", None)
        self._relative_path = data.get("path", None)

        # get all remaining keys as metadata
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
                    _id = neighbour.get("id", None)
                    _name = neighbour.get("name", None)
                    _relative_path = neighbour.get("path", None)

                    # TODO take a look at this if it can be improved
                    _metadata = Metadata(dict(sub.metadata.get_all_items())) or Metadata({})
                    properties = {}
                    for key, value in neighbour.items():
                        if key not in persistent_keys:
                            properties[key] = value

                    _metadata.override(properties)
                    sub_project = sub.__build_sub_project(_name, neighbour, _metadata, _id)
                    # define the path and categories separately
                    sub_project._relative_path = _relative_path

                    # add and override metadata
                    for key, metaitem in sub_project.metadata.items():
                        if neighbour.get(key, None):
                            sub_project.metadata[key].overridden = True

                    visited.append(neighbour)
                    queue.append([sub_project, neighbour.get("subs", [])])

    def __build_sub_project(self,
                            name,
                            parent_sub,
                            metadata,
                            uid
                            ):
        """Build a nested subproject.

        Args:
            name (str): Name of the subproject.
            parent_sub (Subproject): Parent subproject object.
            metadata (Metadata): Metadata object to hold any extra data.
            uid (int): Unique id of the subproject.

        Returns:

        """

        sub_pr = Subproject(name=name,
                            parent_sub=parent_sub,
                            metadata=metadata,
                            uid=uid)
        sub_pr.path = os.path.join(self.path, name)
        self._sub_projects[name] = sub_pr
        return sub_pr

    def add_sub_project(self,
                        name,
                        parent_sub=None,
                        uid=None,
                        **properties
                        ):
        """Add a subproject.
        Requires permissions. Does not create folders or store in
        the persistent database
        Args:
            name (str): Name of the subproject.
            parent_sub (Subproject): Parent subproject object.
            uid (int): Unique id of the subproject.
            **properties (dict): Any extra properties to be added to the subproject.

        Returns:
            Subproject: The newly created subproject object.
        """

        state = self._check_permissions(level=2)
        if state != 1:
            return -1

        if name in self._sub_projects:
            LOG.warning("{0} already exist in sub-projects of {1}".format(name, self._name))
            return -1
            # return 0

        # TODO look at this if it can be improved
        _metadata = Metadata(dict(self.metadata.get_all_items())) or Metadata({})
        # eliminate the None values
        properties = {k: v for k, v in properties.items() if v is not None}
        _metadata.override(properties)

        new_sub = self.__build_sub_project(name,
                                           parent_sub,
                                           _metadata,
                                           uid)  # keep uid at the end

        return new_sub

        # # TODO Currently the overriden uid is not getting checked if it is really unique or not

    def scan_tasks(self):
        """Scan the subproject for tasks."""
        _tasks_search_dir = self.get_abs_database_path()
        _task_paths = glob(os.path.join(_tasks_search_dir, '*.ttask'))

        # add the file if it is new. if it is not new, check the modified time and update if necessary
        for _task_path in _task_paths:
            _task_name = os.path.basename(_task_path).split(".")[0]
            existing_task = self._tasks.get(_task_name, None)
            if not existing_task:
                _task = Task(absolute_path=_task_path, parent_sub=self)
                self._tasks[_task_name] = _task
            else:
                if existing_task.is_modified():
                    existing_task.reload()
        return self._tasks

    def add_task(self, name, categories, task_type=None):
        """
        Add a task to the subproject.
        Args:
            name (str): Name of the task.
            categories (list): List of categories.
            task_type (str): Type of the task.

        Returns:
            Task: The newly created task object.

        """
        # inherit the task type from the parent subproject 'mode' if not specified
        task_type = task_type or self.metadata.get_value("mode", None)
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        file_name = "{0}.ttask".format(name)
        relative_path = os.path.join(self.path, file_name)
        abs_path = os.path.join(self.guard.database_root, relative_path)
        if os.path.exists(abs_path):
            LOG.warning("There is a task under this sub-project with the same name => %s" % name)
            return -1

        _task = Task(abs_path, name=name, categories=categories, path=self.path, file_name=file_name,
                     task_type=task_type, parent_sub=self)
        _task.add_property("name", name)
        _task.add_property("creator", self.guard.user)
        _task.add_property("type", task_type)
        _task.add_property("task_id", _task.id)
        _task.add_property("categories", categories)
        _task.add_property("path", self.path)
        _task.add_property("file_name", file_name)
        _task.apply_settings()
        self._tasks[name] = _task
        return _task

    # def edit_task(self, name, new_name=None, categories=None, task_type=None):
    #     """Edit a task."""
    #     # find the task
    #     _task = self._tasks.get(name, None)
    #     if not _task:
    #         LOG.warning("Task not found")
    #         return -1
    #     # check if the new name is already taken
    #     if new_name and new_name != name:
    #         if new_name in self._tasks:
    #             LOG.warning("Task with the same name already exist")
    #             return -1
    #         # rename the task
    #         _task.(new_name)
    #         self._tasks[new_name] = _task
    #         del self._tasks[name]

    @staticmethod
    def is_task_empty(task):
        """Check all categories and return True if all are empty."""
        for category in task.categories:
            if not task.categories[category].is_empty():
                return False
        return True

    def delete_task(self, task_name):
        """Delete the task from the subproject."""
        # first get the task
        task = self._tasks.get(task_name, None)
        if not task:
            LOG.warning("There is no task with the name => %s" % task_name)
            return -1

        # check all categories are empty
        _is_empty = self.is_task_empty(task)
        permission_level = 2 if _is_empty else 3
        state = self._check_permissions(level=permission_level)
        if state != 1:
            return -1

        self._tasks.pop(task_name)


        # move everything to the purgatory
        if not _is_empty:
            LOG.warning("Sending task {} and everything underneath to purgatory.".format(task_name))
            from tik_manager4.core import io
            io.IO().folder_check(self.get_purgatory_database_path(task.file_name))
            io.IO().folder_check(self.get_purgatory_project_path())
            shutil.move(self.get_abs_database_path(task.file_name), self.get_purgatory_database_path(task.file_name))
            shutil.move(self.get_abs_project_path(), self.get_purgatory_project_path())
        else: # if the task is empty, just delete the database file
            os.remove(task.settings_file)

        return 1

    def find_sub_by_id(self, uid):
        """Find the subproject by id."""
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.id == uid:
                return current
            else:
                queue.extend(list(current.subs.values()))
        LOG.warning("Requested uid does not exist")
        return -1

    def find_sub_by_path(self, path):
        """Find the subproject by path."""
        if path == "":  # this is root
            return self
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.path == path:
                return current
            else:
                queue.extend(list(current.subs.values()))
        LOG.warning("Requested path does not exist")
        return -1

    def find_subs_by_wildcard(self, wildcard):
        """Find the subproject by wildcard."""
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
        """Get the uid of the subproject by path."""
        sub = self.find_sub_by_path(path)
        return sub.id if sub != -1 else sub

    def get_path_by_uid(self, uid):
        """Get the path of the subproject by uid."""
        sub = self.find_sub_by_id(uid)
        return sub.path if sub != -1 else sub

    @staticmethod
    def is_subproject_empty(sub):
        """Check if the subproject has other subprojects or tasks."""
        sub.scan_tasks()
        return not sub.subs and not sub.tasks

    def _remove_sub_project(self, uid=None, path=None):
        """Removes the subproject from the object but not from the database"""

        if not uid and not path:
            LOG.error("Deleting sub project requires at least an id or path ")
            return -1

        # Minimum required permission level is 2
        state = self._check_permissions(level=2)
        if state != 1:
            return -1

        if uid:
            kill_sub = self.find_sub_by_id(uid)
        else:
            kill_sub = self.find_sub_by_path(path)

        if kill_sub == -1:
            LOG.warning("Subproject cannot be found")
            return -1

        # if the subproject is not empty, we need to have level 3
        if not self.is_subproject_empty(kill_sub):
            state = self._check_permissions(level=3)
            if state != 1:
                return -1

        parent_path = os.path.dirname(kill_sub.path) or ""
        parent_sub = self.find_sub_by_path(parent_path)
        del parent_sub.subs[kill_sub.name]

        return 1

    def _delete_folders(self, root, sub=None):
        """Delete the folders of the subproject."""
        sub = sub or self
        folder = os.path.normpath(os.path.join(root, sub.path))
        shutil.rmtree(folder)

    def create_folders(self, root, sub=None):
        """Create folders for subprojects and categories below this starting from 'root' path"""
        sub = sub or self
        folder = os.path.join(root, sub.path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        _ = [sub.create_folders(root, sub=sub) for sub in sub.subs.values()]
