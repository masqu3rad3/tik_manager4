# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Module for Category object.

Category object is responsible for handling the works and publishes under a task.
"""

from pathlib import Path
from fnmatch import fnmatch

from tik_manager4.core.constants import ObjectType
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.work import Work
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Category(Entity):
    """Category object to handle works and publishes under a task."""
    object_type = ObjectType.CATEGORY
    def __init__(self, parent_task, definition=None, **kwargs):
        """Initializes the Category object."""
        super().__init__(**kwargs)
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
        """Return the works under the category."""
        self.scan_works()
        return self._works

    def get_works_by_wildcard(self, wildcard):
        """Return a list of works that match the wildcard.

        Args:
            wildcard (str): The wildcard to match.

        Returns:
            list: List of works that match the wildcard.
        """
        matched_items = []
        for work in self.works.values():
            if fnmatch(work.name, wildcard):
                matched_items.append(work)
        return matched_items

    def scan_works(self):
        """Scan the category folder and return the works.

        Returns:
            dict: Dictionary of works under the category.
        """
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
        """Check if the category is empty.

        Returns:
            bool: True if the category is empty, False otherwise.
        """
        return not bool(self.works)

    def __add_work_properties(self, work, name, dcc, dcc_version, relative_path):
        """Create the properties for the work."""
        work.add_property("name", name)
        work.add_property("creator", self.guard.user)
        work.add_property("category", self.name)
        work.add_property("dcc", dcc)
        work.add_property("dcc_version", dcc_version)
        work.add_property("versions", [])
        work.add_property("work_id", work.generate_id())
        work.add_property("task_name", self.parent_task.name)
        work.add_property("task_id", self.parent_task.id)
        work.add_property("path", relative_path)
        work.add_property("state", "active")
        work.init_properties()

    def create_work_from_path(self, name, file_path, notes="", ignore_checks=True):
        """Register a given path (file or folder) as a work.

        Args:
            name (str): Name of the work.
            file_path (str): Path to the file or folder.
            notes (str): Notes for the work.
            ignore_checks (bool): If True, the checks for the work creation.
                    will be ignored.

        Returns:
            tik_manager4.objects.work: Work object.
        """
        _ignore_checks = ignore_checks
        constructed_name = self.construct_name(name)
        # creating work from an arbitrary path is always considered as a 'standalone' process
        abs_path = self.get_abs_database_path("standalone", f"{constructed_name}.twork")
        if Path(abs_path).exists():
            # in that case instantiate the work and iterate the version.
            work = Work(absolute_path=abs_path, parent_task=self.parent_task)
            work.new_version_from_path(file_path=file_path, notes=notes)
            return work

        relative_path = self.get_relative_work_path(override_dcc="standalone")
        work = Work(abs_path, name=constructed_name, path=relative_path, parent_task=self.parent_task)

        self.__add_work_properties(work, constructed_name, "standalone", "NA", relative_path)
        work.new_version_from_path(file_path=file_path, notes=notes)
        return work

    def create_work_from_template(self, name, template_file, dcc, notes="", ignore_checks=True):
        """ Creates a task under the category.

        Args:
            name (str): Name of the work
            template_file (str): Path to the template file
            dcc (str): DCC name.
            notes (str): Notes for the work
            ignore_checks (bool): Ignore the checks for the work creation

        Returns:
            tik_manager4.objects.work: Work object
        """
        _ignore_checks = ignore_checks
        constructed_name = self.construct_name(name)
        abs_path = self.get_abs_database_path(dcc, f"{constructed_name}.twork")

        if Path(abs_path).exists():
            # in that case instantiate the work and iterate the version.
            work = Work(absolute_path=abs_path, parent_task=self.parent_task)
            work.new_version_from_path(file_path=template_file, notes=notes)
            return work

        relative_path = self.get_relative_work_path(override_dcc=dcc)
        work = Work(abs_path, name=constructed_name, path=relative_path, parent_task=self.parent_task)

        self.__add_work_properties(work, constructed_name, dcc, "NA", relative_path)
        work.new_version_from_path(file_path=template_file, notes=notes)
        return work

    def create_work(self, name, file_format=None, notes="", ignore_checks=True):
        """Create a work under the category.

        Args:
            name (str): Name of the work.
            file_format (str): File format of the work.
            notes (str): Notes for the work.
            ignore_checks (bool): If True, the checks for the work creation.
                    will be ignored.

        Returns:
            tik_manager4.objects.work: Work object.
        """

        # valid file_format keyword can be collected from main.dcc.formats
        state = self.check_permissions(level=1)
        if state != 1:
            return -1

        constructed_name = self.construct_name(name)
        abs_path = self.get_abs_database_path(self.guard.dcc, f"{constructed_name}.twork")
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

        self.__add_work_properties(work, constructed_name, self.guard.dcc, work._dcc_handler.get_dcc_version(), relative_path)
        work.new_version(file_format=file_format, notes=notes, ignore_checks=ignore_checks)
        return work

    def get_relative_work_path(self, override_dcc=None):
        """Return the relative path of the category.

        Args:
            override_dcc (str): If provided, the resolved dcc
                will be overridden with this value.

        Returns:
            str: Relative path of the category.
        """
        dcc = override_dcc or self.guard.dcc
        return Path(self.path, dcc).as_posix()

    def construct_name(self, name):
        """Construct the name for the work file.

        Useful to preview in UI.

        Args:
            name (str): Name of the work.

        Returns:
            str: Constructed name.
        """
        parts = [self.parent_task.name, self.name]
        if name:
            parts.append(name)
        return "_".join(parts)
