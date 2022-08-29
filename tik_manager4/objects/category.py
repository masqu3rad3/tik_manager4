# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

import os
from glob import glob

from tik_manager4.objects.entity import Entity
from tik_manager4.objects.work import Work
from tik_manager4.core import filelog


log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Category(Entity):
    def __init__(self, parent_task=None,  **kwargs):
        super(Category, self).__init__(**kwargs)

        # self._name = name
        self._works = {}
        self._publishes = {}
        self.type = "category"
        self.parent_task = parent_task
        self._relative_path = os.path.join(self.parent_task._relative_path, self.name)
        # print("-"*30)
        # print("-"*30)
        # print("-"*30)
        # print(self._relative_path)

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

        # add the file if its new. if its not new, check the modified time and update if necessary
        for _work_path in _work_paths:
            existing_work = self._works.get(_work_path, None)
            if not existing_work:
                _work = Work(absolute_path=_work_path)
                self._works[_work_path] = _work
            else:
                if existing_work.is_modified():
                    existing_work.reload()

    # def get_modified_time(self, file_path):
    #     """Get the modified time of the file"""
    #     return os.path.getmtime(file_path)



    def add_work(self, name):
        """Creates a task under the category"""
        state = self._check_permissions(level=1)
        if state != 1:
            return -1

        # relative_path = os.path.join(self.path, "%s.twork" % name)
        # abs_path = os.path.join(self._guard.database_root, relative_path)
        contructed_name = self.construct_name(name)
        abs_path = self.get_abs_database_path("%s.twork" % contructed_name)
        if os.path.exists(abs_path):
            log.warning("There is a work under this category with the same name => %s" % contructed_name)
            return -1
        _work = Work(abs_path, name=contructed_name, path=self.path)
        _work.add_property("name", contructed_name)
        _work.add_property("creator", self._guard.user)
        _work.add_property("category", self.name)
        # _task.add_property("dcc", dcc)
        _work.add_property("dcc", self._guard.dcc)
        _work.add_property("versions", [])
        _work.add_property("task_id", _work.id)
        _work.add_property("path", self.path)
        _work.apply_settings()
        return _work

    def construct_name(self, name):
        """Constructs the name for the work file"""
        return "{0}_{1}_{2}".format(self.parent_task.name, self.name, name)