"""Extract Alembic from Maya scene"""

import maya.cmds as cmds
from tik_manager4.dcc.extract_core import ExtractCore

class Alembic(ExtractCore):
    """Extract Alembic from Maya scene"""

    def __init__(self):
        super(ExtractCore).__init__()
        self.name: str = ""
        self._output_path: str = ""
        self._category: str = ""

        self.category_functions = {
            "model": self.extract_model
        }

    def extract(self):
        func = self.category_functions.get(self.category, self.extract_default)
        pass

    def extract_model(self):
        pass

    def extract_default(self):
        """Extract method for any non-specified category"""
        pass

