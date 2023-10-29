"""Template module for publishing"""
import os
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class ExtractCore(object):
    def __init__(self):
        self._output_path: str = ""
        self._category: str = ""
        self._status = "idle"

        self.category_functions = {}

    @property
    def status(self):
        return self._status

    @property
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, file_path):
        if os.path.isfile(file_path):
            self._output_path = file_path
        else:
            raise ValueError(f"Path is not a file. Given path: {file_path}")

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        # TODO some validation here
        self._category = category

    def extract(self):
        func = self.category_functions.get(self.category, self._extract_default)
        try:
            func()
        except Exception as e:
            LOG.error(e)
            LOG.error(f"Error while extracting {self.name} to {self.output_path}")
            self._status = "error"
        self._status = "extracted"

    def _extract_default(self):
        """Extract method for any non-specified category"""
        pass
