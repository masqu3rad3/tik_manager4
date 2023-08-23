# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

import os
from glob import glob
from fnmatch import fnmatch

from tik_manager4.objects.entity import Entity
from tik_manager4.objects.work import Work
from tik_manager4.core import filelog


log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Category(Entity):
    def __init__(self, parent_task, definition=None, **kwargs):
        super(Category, self).__init__(**kwargs)
        definition = definition or {}
        self._works = {}
        self._publishes = {}
        self.type = definition.get("type", None)
        self.display_name = definition.get("display_name", None)
        self.validations = definition.get("validate", [])
        self.extracts = definition.get("extracts", [])
        self.parent_task = parent_task
        self._relative_path = os.path.join(
            self.parent_task._relative_path, self.parent_task.name, self.name
        )

    @property
    def works(self):
        self.scan_works()
        return self._works

    def get_works_by_wildcard(self, wildcard):
        """Return a list of works that match the wildcard."""
        matched_items = []
        for work in self.works.values():
            if fnmatch(work.name, wildcard):
                print(work.name)
                matched_items.append(work)
        return matched_items

    @property
    def publishes(self):
        self.scan_publishes()
        return self._publishes

    def scan_publishes(self):
        pass

    def scan_works(self, all_dcc=False):
        if self.guard.dcc == "Standalone":
            all_dcc = True

        # get all the files in directory with .twork extension
        if not all_dcc:
            _search_dir = self.get_abs_database_path(self.guard.dcc)
            _work_paths = glob(os.path.join(_search_dir, "*.twork"), recursive=False)

        # get all the files in a directory recursively with .twork extension
        else:
            _search_dir = self.get_abs_database_path()
            _work_paths = glob(
                os.path.join(_search_dir, "**", "*.twork"), recursive=True
            )

        # add the file if it is new. if it is not new,
        # check the modified time and update if necessary
        for _w_path, _w_data in dict(self._works).items():
            if _w_path not in _work_paths:
                self._works.pop(_w_path)
        for _work_path in _work_paths:
            existing_work = self._works.get(_work_path, None)
            if not existing_work:
                _work = Work(absolute_path=_work_path)
                self._works[_work_path] = _work
            else:
                if existing_work.is_modified():
                    existing_work.reload()
        return self._works

    def is_empty(self):
        """Check if the category is empty"""
        return not bool(self.works)

    def create_work(self, name, file_format=None, notes=""):
        """Creates a task under the category"""

        # valid file_format keyword can be collected from main.dcc.formats
        state = self.check_permissions(level=1)
        if state != 1:
            return -1

        contructed_name = self.construct_name(name)
        relative_path = os.path.join(self.path, self.guard.dcc).replace("\\", "/")
        abs_path = self.get_abs_database_path(
            self.guard.dcc, "%s.twork" % contructed_name
        )
        if os.path.exists(abs_path):
            # in that case instantiate the work and iterate the version.
            _work = Work(absolute_path=abs_path)
            _work.new_version(file_format=file_format, notes=notes)
            return _work
        _work = Work(abs_path, name=contructed_name, path=relative_path)
        _work.add_property("name", contructed_name)
        _work.add_property("creator", self.guard.user)
        _work.add_property("category", self.name)
        _work.add_property("dcc", self.guard.dcc)
        _work.add_property("versions", [])
        _work.add_property("work_id", _work.generate_id())
        _work.add_property("task_name", self.parent_task.name)
        _work.add_property("task_id", self.parent_task.id)
        _work.add_property("path", relative_path)
        _work.add_property("state", "working")
        _work.new_version(file_format=file_format, notes=notes)
        return _work

    def delete_work(self, name):
        """Delete a work under the category."""

        _work = self._works.get(name, None)
        if not _work:
            log.warning(
                "There is no work under this category with the name => %s" % name
            )
            return -1

        # if not, check if the user is the owner of the work
        if self.guard.user != _work.creator or self.check_permissions(level=3):
            log.warning("You do not have the permission to delete this work")
            return -1

        del self._works[name]
        _work.delete()

    def construct_name(self, name):
        """Construct the name for the work file. Useful to preview in UI."""
        return "{0}_{1}_{2}".format(self.parent_task.name, self.name, name)
