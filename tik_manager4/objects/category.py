# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

import os
from glob import glob

from tik_manager4.objects.entity import Entity
from tik_manager4.core import filelog

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Category(Entity):
    def __init__(self, parent_task=None,  **kwargs):
        super(Category, self).__init__(**kwargs)

        # self._name = name
        self._works = []
        self._publishes = []
        self.type = "category"
        self.parent_task = parent_task

    @property
    def works(self):
        return self._works

    @property
    def publishes(self):
        return self._publishes

    def scan_works(self, all_dcc=False):
        if self._guard.dcc == "Standalone":
            all_dcc = True

        if not all_dcc:
            _works_search_dir = self.get_abs_database_path(self._guard.dcc, "work")  # this is DCC specific directory
            _work_paths = glob(os.path.join(_works_search_dir, '*.twork'))
        else:
            _search_dir = self.get_abs_database_path()
            _work_paths = [y for x in os.walk(_search_dir) for y in glob(os.path.join(x[0], '*.twork'))]


    # def add_task(self, name):
    #     """Creates a task under the category"""
    #     state = self._check_permissions(level=1)
    #     if state != 1:
    #         return -1
    #     relative_path = os.path.join(self.path, "%s.ttask" % name)
    #     abs_path = os.path.join(self._guard.database_root, relative_path)
    #     if os.path.exists(abs_path):
    #         log.warning("There is a task under this category with the same name => %s" % name)
    #         return -1
    #     _task = Task(abs_path, name=name, category=self.name, path=self.path)
    #     _task.add_property("name", name)
    #     _task.add_property("creator", self._guard.user)
    #     _task.add_property("category", self.name)
    #     # _task.add_property("dcc", dcc)
    #     # _task.add_property("versions", [])
    #     # _task.add_property("publishes", [])
    #     _task.add_property("task_id", _task.id)
    #     _task.add_property("path", self.path)
    #     _task.apply_settings()
    #     return _task

