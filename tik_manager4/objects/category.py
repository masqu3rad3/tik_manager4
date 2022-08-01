import os
from glob import glob
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.task import Task
from tik_manager4.core import filelog

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Category(Entity):
    def __init__(self, name="", *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)

        self._name = name
        self._tasks = []
        self.type = "category"

    @property
    def tasks(self):
        return self._tasks or self.scan_tasks()

    def scan_tasks(self):
        self._tasks.clear()
        # _search_dir = os.path.join(self._guard.database_root, self.path)
        _search_dir = self.get_abs_database_path()
        _task_paths = glob(os.path.join(_search_dir, '*.ttask'))
        for b_path in _task_paths:
            self._tasks.append(Task(b_path))

        # return glob(os.path.join(_search_dir, '*.tbs'))

    def add_task(self, name):
        """Creates a task under the category"""
        state = self._check_permissions(level=1)
        if state != 1:
            return -1
        relative_path = os.path.join(self.path, "%s.ttask" % name)
        abs_path = os.path.join(self._guard.database_root, relative_path)
        if os.path.exists(abs_path):
            log.warning("There is a task under this category with the same name => %s" % name)
            return -1
        _task = Task(abs_path, name=name, category=self.name, path=self.path)
        _task.add_property("name", name)
        _task.add_property("creator", self._guard.user)
        _task.add_property("category", self.name)
        # _task.add_property("dcc", dcc)
        # _task.add_property("versions", [])
        # _task.add_property("publishes", [])
        _task.add_property("referenceID", None)
        _task.add_property("path", self.path)
        _task.apply_settings()
        return _task

