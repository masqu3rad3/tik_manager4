"""Core file for inserting elements into the scenes."""

import importlib
from pathlib import Path
from tik_manager4.core import filelog
from tik_manager4.objects.metadata import Metadata

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class IngestCore:
    """Core class for ingesting elements into the scene."""

    nice_name: str = ""
    valid_extensions: list = []
    importable: bool = True
    referencable: bool = True

    def __init__(self):
        self.name = str(Path(__file__).stem)
        self._category: str = ""
        self._status: str = "idle"
        self._file_path: str = ""
        self._namespace: str = ""
        self._metadata: Metadata
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
        """Set the category for the rules."""
        # TODO some validation here
        self._category = category

    @property
    def state(self):
        """Return the state of the ingest."""
        return self._status

    @property
    def ingest_path(self):
        """Return the file path of the ingest."""
        return self._file_path

    @property
    def namespace(self):
        """Return the namespace of the ingest."""
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        """Set the namespace of the ingest."""
        self._namespace = namespace

    @property
    def metadata(self):
        """Return the metadata object."""
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Set the metadata object."""
        self._metadata = metadata

    @ingest_path.setter
    def ingest_path(self, ingest_path):
        """Set the path for the ingest.
        Starting from version 4.1.2, this can only be a file.
        """
        _path = Path(ingest_path)
        if not _path.is_file():
            raise ValueError(f"Path is not a file: {ingest_path}")
        if _path.suffix not in self.valid_extensions:
            raise ValueError(f"File extension not valid: {_path.suffix}")
        self._file_path = ingest_path

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
