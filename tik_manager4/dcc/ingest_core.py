"""Core file for inserting elements into the scenes."""

import importlib
from pathlib import Path
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class IngestCore:
    """Core class for ingesting elements into the scene."""

    nice_name: str = ""
    valid_extensions: list = []

    def __init__(self):
        self.name = str(Path(__file__).stem)
        self._category: str = ""
        self._status: str = "idle"
        self._file_path: str = ""
        self._namespace: str = ""
        self.category_functions: dict = {}
        self.category_reference_functions: dict = {}

    def __init_subclass__(cls, **kwargs):
        # Get the base name of the file without the extension using pathlib
        module = importlib.import_module(cls.__module__)
        module_file_path = Path(module.__file__).resolve()
        module_name = module_file_path.stem
        # Set the 'name' variable in the subclass
        cls.name = module_name
        super().__init_subclass__(**kwargs)

    @property
    def category(self):
        """Return the category for the rules."""
        return self._category

    @category.setter
    def category(self, category):
        # TODO some validation here
        self._category = category

    @property
    def state(self):
        return self._status

    @property
    def file_path(self):
        return self._file_path

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace

    @file_path.setter
    def file_path(self, file_path):
        _file_path = Path(file_path)
        if not _file_path.exists():
            raise ValueError(f"File path does not exist: {file_path}")
        if _file_path.suffix not in self.valid_extensions:
            raise ValueError(f"File extension not valid: {_file_path.suffix}")
        self._file_path = file_path

    def bring_in(self):  # a.k.a import
        """Bring in the element to the scene."""
        func = self.category_functions.get(self.category, self._bring_in_default)
        try:
            func()
            self._status = "success"
        except Exception as exc:  # pylint: disable=broad-except
            LOG.error(exc)
            self._status = "failed"

    def reference(self):
        """Reference the element to the scene where available."""
        func = self.category_reference_functions.get(
            self.category, self._reference_default
        )
        try:
            func()
            self._status = "success"
        except Exception as exc:  # pylint: disable=broad-except
            LOG.error(exc)
            self._status = "failed"

    def _bring_in_default(self):
        """Bring in method for any non-specified category"""
        LOG.warning(f"Bring in not implemented for {self.name}")

    def _reference_default(self):
        """Reference method for any non-specified category"""
        LOG.warning(f"Reference not implemented for {self.name}")
