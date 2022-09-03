# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

from glob import glob
import os
import shutil

from fnmatch import fnmatch
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.task import Task
# from tik_manager4.objects.category import Category

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Subproject(Entity):
    def __init__(self, parent_sub=None, resolution=None, fps=None, mode=None, shot_data=None, **kwargs):
        super(Subproject, self).__init__(**kwargs)
        self.__fps = fps
        self.__resolution = resolution
        self.__mode = mode
        self.__shot_data = shot_data
        self.__parent_sub = parent_sub
        self._sub_projects = {}
        self._tasks = {}
        # self._categories = []

    @property
    def parent(self):
        return self.__parent_sub

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value

    @property
    def shot_data(self):
        return self.__shot_data

    @shot_data.setter
    def shot_data(self, value):
        self.__shot_data = value

    @property
    def subs(self):
        return self._sub_projects

    @property
    def tasks(self):
        return self._tasks

    @property
    def resolution(self):
        return self.__resolution

    @property
    def fps(self):
        return self.__fps

    def set_resolution(self, val):
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if isinstance(val, (list, tuple)):
            self.__resolution = val
            return 1
        msg = "%s is not a valid resolution. must be list or tuple." % val
        LOG.error(msg, proceed=False)

    def set_fps(self, val):
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if isinstance(val, (int, float)):
            self.__fps = val
            return 1
        msg = "%s is not a valid fps value. must be int or float." % val
        LOG.error(msg, proceed=False)

    def get_sub_tree(self):
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
                        # "mode": neighbour.mode,
                        # "resolution": neighbour.resolution,
                        # "fps": neighbour.fps,
                        # "categories": list(neighbour.categories.keys()),
                        # "categories": [category.name for category in neighbour.categories],
                        # "categories": [{"name": category.name, "id": category.id} for category in neighbour.categories],
                        "subs": [],  # this will be filled with the while loop
                    }
                    if neighbour.resolution != self.resolution:
                        sub_data["resolution"] = neighbour.resolution
                    if neighbour.fps != self.fps:
                        sub_data["fps"] = neighbour.fps
                    if neighbour.mode != self.mode:
                        sub_data["mode"] = neighbour.mode
                    if neighbour.shot_data != self.shot_data:
                        sub_data["shot_data"] = neighbour.shot_data
                    parent["subs"].append(sub_data)

                    visited.append(neighbour)
                    queue.append([sub_data, neighbour])

        return all_data

    def set_sub_tree(self, data):
        """
        Creates the subproject from the data dictionary.
        This is for building back the hierarchy from json data

        """
        visited = []
        queue = []
        self.id = data.get("id", None)
        self._name = data.get("name", None)
        self._relative_path = data.get("path", None)
        self.__resolution = data.get("resolution", None)
        self.__fps = data.get("fps", None)
        self.__mode = data.get("mode", None)
        self.__shot_data = data.get("shot_data", None)
        # _ = [self.__build_category(x) for x in data.get("categories", [])]

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
                    _resolution = neighbour.get("resolution", self.resolution)
                    _fps = neighbour.get("fps", self.fps)
                    _mode = neighbour.get("mode", self.mode)
                    _shot_data = neighbour.get("shot_data", self.shot_data)
                    # _categories = neighbour.get("categories", [])
                    sub_project = sub.__build_sub_project(_name, neighbour, _resolution, _fps, _mode, _shot_data, _id)
                    # define the path and categories separately
                    sub_project._relative_path = _relative_path
                    # _ = [sub_project.__build_category(x) for x in _categories]
                    # _ = [sub_project.__build_category(x.get("name", None), x.get("id", None)) for x in _categories]

                    visited.append(neighbour)
                    queue.append([sub_project, neighbour.get("subs", [])])
    def __build_sub_project(self, name, parent_sub, resolution, fps, mode, shot_data, uid):
        """Builds the sub-project inside class."""

        sub_pr = Subproject(name=name, parent_sub=parent_sub, resolution=resolution, fps=fps, mode=mode, shot_data=shot_data, uid=uid)
        sub_pr.path = os.path.join(self.path, name)
        self._sub_projects[name] = sub_pr
        return sub_pr
    def add_sub_project(self, name, parent_sub=None, resolution=None, fps=None, mode=None, shot_data=None, uid=None):
        """
        Adds a sub project. requires permissions. Does not create folders or store in the persistent database

        """

        state = self._check_permissions(level=2)
        if state != 1:
            return -1

        if name in self._sub_projects:
            LOG.warning("{0} already exist in sub-projects of {1}".format(name, self._name))
            return -1
            # return 0

        # inherit the resolution and fps if not overriden
        resolution = resolution or self.resolution
        fps = fps or self.fps
        mode = mode or self.mode

        return self.__build_sub_project(name, parent_sub, resolution, fps, mode, shot_data, uid)  # keep uid at the end

        # # TODO Currently the overriden uid is not getting checked if it is really unique or not
        # sub_pr = Subproject(name=name, resolution=resolution, fps=fps, uid=uid)
        # # sub_pr._relative_path = os.path.join(self._relative_path, name)
        # sub_pr.path = os.path.join(self.path, name)
        # self._sub_projects[name] = sub_pr
        # return sub_pr

    def scan_tasks(self):
        _tasks_search_dir = self.get_abs_database_path()
        _task_paths = glob(os.path.join(_tasks_search_dir, '*.ttask'))

        # add the file if it is new. if it is not new, check the modified time and update if necessary
        for _task_path in _task_paths:
            _task_name = os.path.basename(_task_path).split(".")[0]
            existing_task = self._tasks.get(_task_name, None)
            if not existing_task:
                _task = Task(absolute_path=_task_path)
                self._tasks[_task_name] = _task
            else:
                if existing_task.is_modified():
                    existing_task.reload()
        return self._tasks

    def add_task(self, name, categories, task_type=None):
        """Creates a task under the category"""
        task_type = task_type or self.__mode
        # if not categories:
        #     if not mode
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        relative_path = os.path.join(self.path, "%s.ttask" % name)
        abs_path = os.path.join(self.guard.database_root, relative_path)
        if os.path.exists(abs_path):
            LOG.warning("There is a task under this sub-project with the same name => %s" % name)
            return -1

        _task = Task(abs_path, name=name, categories=categories, path=self.path, task_type=task_type)
        _task.add_property("name", name)
        _task.add_property("creator", self.guard.user)
        _task.add_property("type", task_type)
        _task.add_property("task_id", _task.id)
        _task.add_property("categories", categories)
        _task.add_property("path", self.path)
        _task.apply_settings()
        self._tasks[name] = _task
        return _task

    def find_sub_by_id(self, uid):
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
        sub = self.find_sub_by_path(path)
        return sub.id if sub != -1 else sub

    def get_path_by_uid(self, uid):
        sub = self.find_sub_by_id(uid)
        return sub.path if sub != -1 else sub

    def _remove_sub_project(self, uid=None, path=None):
        """Removes the sub project from the object but not from the database"""

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
        sub = sub or self
        folder = os.path.join(root, sub.path)
        shutil.rmtree(folder)

    def create_folders(self, root, sub=None):
        """Creates folders for subprojects and categories below this starting from 'root' path"""
        sub = sub or self
        folder = os.path.join(root, sub.path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # unfortunately python 2.x does not support  exist_ok argument...
        # for category in sub.categories:
        #     _f = os.path.join(folder, category.name)
        #     if not os.path.exists(_f):
        #         os.makedirs(_f)
        _ = [sub.create_folders(root, sub=sub) for sub in sub.subs.values()]
