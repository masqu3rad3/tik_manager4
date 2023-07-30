"""Template module for publishing"""
import os

class ExtractCore(object):
    def __init__(self):
        self.name: str = ""
        self._output_path: str = ""
        self._category: str = ""

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
        pass
