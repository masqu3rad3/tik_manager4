"""Extract Alembic from Maya scene"""

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.extract_core import ExtractCore

# The Collector will only collect classes inherit ExtractCore
class Alembic(ExtractCore):
    """Extract Alembic from Maya scene"""
    name = "alembic" # IMPORTANT. Must match to the one in category_definitions.json
    def __init__(self):
        super(ExtractCore).__init__()
        om.MGlobal.displayInfo("Alembic Extractor loaded")
        self.name: str = ""
        self._output_path: str = ""
        self._category: str = ""

        self.category_functions = {"model": self._extract_model,
                                   "animation": self._extract_animation,
                                   "fx": self._extract_fx}

    def extract(self):
        func = self.category_functions.get(self.category, self._extract_default)
        pass

    def _extract_model(self):
        """Extract method for model category"""
        pass

    def _extract_animation(self):
        """Extract method for animation category"""
        pass

    def _extract_fx(self):
        """Extract method for fx category"""
        pass

    def _extract_default(self):
        """Extract method for any non-specified category"""
        pass
