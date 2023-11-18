"""Template module for publishing"""
# import os
from pathlib import Path
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class ExtractCore(object):
    def __init__(self):
        self._name: str = ""
        self._extension: str = ""
        self._extract_folder: str = ""
        self._category: str = ""
        self._status = "idle"

        self.category_functions = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, extension):
        self._extension = extension

    @property
    def extract_folder(self):
        return self._extract_folder

    @extract_folder.setter
    def extract_folder(self, folder_path):
        _folder_path_obj = Path(folder_path)
        _folder_path_obj.mkdir(parents=True, exist_ok=True)
        self._extract_folder = str(_folder_path_obj)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        # TODO some validation here
        self._category = category

    @property
    def status(self):
        return self._status

    def extract(self):
        func = self.category_functions.get(self.category, self._extract_default)
        try:
            func()
        except Exception as e:
            LOG.error(e)
            LOG.error(f"Error while extracting {self.name} to {self.extract_folder}")
            self._status = "error"
        self._status = "extracted"

    def _extract_default(self):
        """Extract method for any non-specified category"""
        pass

    def resolve_output(self):
        """Resolve the output path"""
        output_path = Path(self.extract_folder) / f"{self.extract_name}{self.extension}"
        return str(output_path)