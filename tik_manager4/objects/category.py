# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

from pathlib import Path
from fnmatch import fnmatch

from tik_manager4.objects.entity import Entity
from tik_manager4.objects.work import Work
from tik_manager4.core import filelog


LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


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
        self._relative_path = str(Path(self.parent_task._relative_path, self.parent_task.name, self.name))

    @property
    def works(self):
        self.scan_works()
        return self._works

    def get_works_by_wildcard(self, wildcard):
        """Return a list of works that match the wildcard."""
        matched_items = []
        for work in self.works.values():
            if fnmatch(work.name, wildcard):
                matched_items.append(work)
        return matched_items

    def scan_works(self):
        """Scan the category folder and return the works"""
        # get all files recursively, regardless of the dcc
        search_dir = self.get_abs_database_path()
        _work_paths = list(Path(search_dir).rglob("**/*.twork"))

        # add the file if it is new. if it is not new,
        # check the modified time and update if necessary
        for w_path, _w_data in dict(self._works).items():
            if w_path not in _work_paths:
                self._works.pop(w_path)
        for _work_path in _work_paths:
            existing_work = self._works.get(_work_path, None)
            if not existing_work:
                work = Work(absolute_path=_work_path, parent_task=self.parent_task)
                self._works[_work_path] = work
            else:
                if existing_work.is_modified():
                    existing_work.reload()
        return self._works

    def is_empty(self):
        """Check if the category is empty"""
        return not bool(self.works)

    def create_work_from_path(self, name, file_path, notes="", ignore_checks=True):
        """Register a given path (file or folder) as a work"""

        constructed_name = self.construct_name(name)
        # creating work from an arbitrary path is always considered as a 'standalone' process
        abs_path = self.get_abs_database_path("standalone", f"{constructed_name}.twork")
        if Path(abs_path).exists():
            # in that case instantiate the work and iterate the version.
            work = Work(absolute_path=abs_path, parent_task=self.parent_task)
            work.new_version_from_path(file_path=file_path, notes=notes, ignore_checks=ignore_checks)
            return work

        relative_path = self.get_relative_work_path(override_dcc="standalone")
        work = Work(abs_path, name=constructed_name, path=relative_path, parent_task=self.parent_task)

        work.add_property("name", constructed_name)
        work.add_property("creator", self.guard.user)
        work.add_property("category", self.name)
        work.add_property("dcc", "standalone")
        work.add_property("dcc_version", "NA")
        work.add_property("versions", [])
        work.add_property("work_id", work.generate_id())
        work.add_property("task_name", self.parent_task.name)
        work.add_property("task_id", self.parent_task.id)
        work.add_property("path", relative_path)
        work.add_property("state", "working")
        work.init_properties()
        work.new_version_from_path(file_path=file_path, notes=notes, ignore_checks=ignore_checks)
        return work

    def create_work(self, name, file_format=None, notes="", ignore_checks=True):
        """Creates a task under the category"""

        # valid file_format keyword can be collected from main.dcc.formats
        state = self.check_permissions(level=1)
        if state != 1:
            return -1

        constructed_name = self.construct_name(name)
        abs_path = self.get_abs_database_path(self.guard.dcc, f"{constructed_name}.twork")
        # abs_path = self.get_abs_database_path(f"{constructed_name}.twork")
        if Path(abs_path).exists():
            # in that case instantiate the work and iterate the version.
            work = Work(absolute_path=abs_path, parent_task=self.parent_task)
            work.new_version(file_format=file_format, notes=notes, ignore_checks=ignore_checks)
            return work

        relative_path = self.get_relative_work_path()
        work = Work(abs_path, name=constructed_name, path=relative_path, parent_task=self.parent_task)
        if not ignore_checks:
            # check if there is a mismatch with the current dcc version
            dcc_mismatch = work.check_dcc_version_mismatch()
            if dcc_mismatch:
                LOG.warning(
                    f"The current dcc version ({dcc_mismatch[1]}) does not match with the defined dcc version ({dcc_mismatch[0]})."
                )
                return -1

        work.add_property("name", constructed_name)
        work.add_property("creator", self.guard.user)
        work.add_property("category", self.name)
        work.add_property("dcc", self.guard.dcc)
        work.add_property("dcc_version", work._dcc_handler.get_dcc_version())
        work.add_property("versions", [])
        work.add_property("work_id", work.generate_id())
        work.add_property("task_name", self.parent_task.name)
        work.add_property("task_id", self.parent_task.id)
        work.add_property("path", relative_path)
        work.add_property("state", "working")
        work.init_properties()
        work.new_version(file_format=file_format, notes=notes, ignore_checks=ignore_checks)
        return work

    def get_relative_work_path(self, override_dcc=None):
        """Return the relative path of the category"""
        dcc = override_dcc or self.guard.dcc
        return Path(self.path, dcc).as_posix()


    def construct_name(self, name):
        """Construct the name for the work file. Useful to preview in UI."""
        return "{0}_{1}_{2}".format(self.parent_task.name, self.name, name)
