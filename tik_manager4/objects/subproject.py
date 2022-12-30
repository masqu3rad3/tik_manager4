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
    def __init__(self, value, overridden=False):
        self.value = value
        self.overridden = overridden
class Metadata(dict):
    """Metadata class."""
    def __init__(self, data_dictionary):
        super(Metadata, self).__init__(data_dictionary)

        # create a Metaitem for each key in the data_dictionary
        for key, val in data_dictionary.items():
            self.add_item(key, val)

    def add_item(self, key, value):
        """Add an item to the metadata."""
        self[key] = Metaitem(value)
        return self[key]

    def get_all_items(self):
        """Return all items in the metadata."""
        for key, val in self.items():
            yield key, val.value

class Subproject(Entity):
    def __init__(self,
                 parent_sub=None,
                 resolution=None,
                 fps=None,
                 mode=None,
                 shot_data=None,
                 metadata=None,
                 **kwargs):
        super(Subproject, self).__init__(**kwargs)
        self.__fps = fps
        self.__resolution = resolution
        self.__mode = mode
        self.__shot_data = shot_data
        self.__parent_sub = parent_sub
        self._sub_projects = {}
        self._tasks = {}

        metadata = metadata or {}
        self._metadata = Metadata(metadata)

        self.overridden_resolution = False
        self.overridden_fps = False
        self.overridden_mode = False
        self.overridden_shot_data = False

    @property
    def parent(self):
        """Return the parent subproject."""
        return self.__parent_sub

    @property
    def mode(self):
        """Get the mode of the subproject."""
        return self.__mode

    @mode.setter
    def mode(self, value):
        """Set the mode of the subproject."""
        self.__mode = value

    @property
    def shot_data(self):
        """Return the shot data of the subproject."""
        return self.__shot_data

    @shot_data.setter
    def shot_data(self, value):
        """Set the shot data of the subproject."""
        self.__shot_data = value

    @property
    def subs(self):
        """Return the subprojects."""
        return self._sub_projects

    @property
    def tasks(self):
        """Return the tasks of the subproject."""
        return self._tasks

    @property
    def resolution(self):
        """Return the resolution of the subproject."""
        return self.__resolution

    @property
    def fps(self):
        """Return the fps of the subproject."""
        return self.__fps

    @property
    def properties(self):
        """Return the subproject properties as a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "resolution": self.resolution,
            "fps": self.fps,
            "mode": self.mode,
            "shot_data": self.shot_data,
            "overridden_resolution": self.overridden_resolution,
            "overridden_fps": self.overridden_fps,
            "overridden_mode": self.overridden_mode
        }

    @property
    def metadata(self):
        """Return the metadata of the subproject."""
        return self._metadata

    def set_resolution(self, val):
        """Set the resolution of the subproject."""
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if isinstance(val, (list, tuple)):
            self.__resolution = val
            return 1
        msg = "%s is not a valid resolution. must be list or tuple." % val
        LOG.error(msg, proceed=False)

    def set_fps(self, val):
        """Set the fps of the subproject."""
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if isinstance(val, (int, float)):
            self.__fps = val
            return 1
        msg = "%s is not a valid fps value. must be int or float." % val
        LOG.error(msg, proceed=False)

    def set_mode(self, val):
        """Set the mode of the subproject."""
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if isinstance(val, str):
            self.__mode = val
            return 1
        msg = "%s is not a valid mode. must be str." % val
        LOG.error(msg, proceed=False)

    def get_sub_tree(self):
        """Return the subproject tree as a dictionary"""
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "resolution": self.resolution,
            "fps": self.fps,
            "mode": self.mode,
            "shot_data": self.shot_data,
            # "categories": [category.name for category in self.categories],
            "subs": [],  # this will be filled with the while loop
        }

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
                        print("------------------")
                        print("------------------")
                        print(key, metaitem.value)
                        if metaitem.overridden:
                            print("overridden")
                            sub_data[key] = metaitem.value
                        print("------------------")
                        print("------------------")

                    if neighbour.overridden_resolution:
                        sub_data["resolution"] = neighbour.resolution
                    if neighbour.overridden_fps:
                        sub_data["fps"] = neighbour.fps
                    if neighbour.overridden_mode:
                        sub_data["mode"] = neighbour.mode
                    if neighbour.overridden_shot_data:
                        sub_data["shot_data"] = neighbour.shot_data

                    parent["subs"].append(sub_data)

                    visited.append(neighbour)
                    queue.append([sub_data, neighbour])

        return all_data

    def set_sub_tree(self, data):
        """Create the subproject from the data dictionary.
        This is for building back the hierarchy from json data
        """
        # persistent keys
        persistent_keys = ["id", "name", "path", "resolution", "fps", "mode", "shot_data", "subs"]
        visited = []
        queue = []
        self.id = data.get("id", None)
        self._name = data.get("name", None)
        self._relative_path = data.get("path", None)
        self.__resolution = data.get("resolution", None)
        self.__fps = data.get("fps", None)
        self.__mode = data.get("mode", None)
        self.__shot_data = data.get("shot_data", None)

        # get all remaining keys as metadata
        for key, value in data.items():
            if key not in persistent_keys:
                self._metadata.add_item(key, value)

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
                    _resolution = neighbour.get("resolution", sub.resolution)
                    _fps = neighbour.get("fps", sub.fps)
                    _mode = neighbour.get("mode", sub.mode)

                    _shot_data = neighbour.get("shot_data", self.shot_data)

                    _metadata = {} # this will filled after subproject creation
                    for key, value in neighbour.items():
                        if key not in persistent_keys:
                            _metadata[key] = value or sub.metadata.get(key, None)


                    sub_project = sub.__build_sub_project(_name, neighbour, _resolution, _fps, _mode, _shot_data, _metadata, _id)
                    # define the path and categories separately
                    sub_project._relative_path = _relative_path

                    # add and override metadata
                    for key, metaitem in sub_project.metadata.items():
                        if neighbour.get(key, None):
                            # sub_project.metadata.add_item(key, value)
                            sub_project.metadata[key].overridden = True

                    if neighbour.get("resolution", None):
                        sub_project.overridden_resolution = True
                    if neighbour.get("fps", None):
                        sub_project.overridden_fps = True
                    if neighbour.get("mode", None):
                        sub_project.overridden_mode = True
                    if neighbour.get("shot_data", None):
                        sub_project.overridden_shot_data = True

                    visited.append(neighbour)
                    queue.append([sub_project, neighbour.get("subs", [])])

    def __build_sub_project(self,
                            name,
                            parent_sub,
                            resolution,
                            fps,
                            mode,
                            shot_data,
                            metadata,
                            uid
                            ):
        """Build the subproject inside class."""

        sub_pr = Subproject(name=name,
                            parent_sub=parent_sub,
                            resolution=resolution,
                            fps=fps,
                            mode=mode,
                            shot_data=shot_data,
                            metadata=metadata,
                            uid=uid)
        sub_pr.path = os.path.join(self.path, name)
        self._sub_projects[name] = sub_pr
        return sub_pr

    def add_sub_project(self,
                        name,
                        parent_sub=None,
                        resolution=None,
                        fps=None,
                        mode=None,
                        shot_data=None,
                        metadata=None,
                        uid=None
                        ):
        """Add a subproject.
        requires permissions.
        Does not create folders or store in the persistent database
        """

        state = self._check_permissions(level=2)
        if state != 1:
            return -1

        if name in self._sub_projects:
            LOG.warning("{0} already exist in sub-projects of {1}".format(name, self._name))
            return -1
            # return 0

        # inherit the resolution, fps, mode and shot_data if not overriden
        _resolution = resolution or self.resolution
        _fps = fps or self.fps
        _mode = mode or self.mode
        _shot_data = shot_data or self.shot_data

        # TODO this sandviching of the metadata is not good
        # TODO try to find a better way to do this
        metadata = metadata or {}
        _inherited_metadata = metadata.copy()
        # inherit the metadata from the parent
        for key, metaitem in self.metadata.items():
            if key not in metadata:
                _inherited_metadata[key] = metaitem.value

        new_sub = self.__build_sub_project(name, parent_sub, _resolution, _fps, _mode, _shot_data, _inherited_metadata,
                                           uid)  # keep uid at the end
        # override the metadata if its found in the metadata dictionary
        for key, metaitem in new_sub.metadata.items():
            if metadata.get(key, None):
                # new_sub.metadata.add_item(key, value)
                new_sub.metadata[key].overridden = True
        new_sub.overridden_resolution = bool(resolution)
        new_sub.overridden_fps = bool(fps)
        new_sub.overridden_mode = bool(mode)
        new_sub.overridden_shot_data = bool(shot_data)

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
        """Create a task."""
        task_type = task_type or self.__mode
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

    @staticmethod
    def __is_task_empty(task):
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
        _is_empty = self.__is_task_empty(task)
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

    def _remove_sub_project(self, uid=None, path=None):
        """Removes the subproject from the object but not from the database"""

        if not uid and not path:
            LOG.error("Deleting sub project requires at least an id or path ")
            return -1

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
