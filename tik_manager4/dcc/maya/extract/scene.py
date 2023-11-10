"""Extract Maya scene."""

import pathlib
from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.extract_core import ExtractCore

# The Collector will only collect classes inherit ExtractCore
class Scene(ExtractCore):
    """Extract Alembic from Maya scene"""
    name = "scene" # IMPORTANT. Must match to the one in category_definitions.json
    def __init__(self):
        super(ExtractCore).__init__()
        om.MGlobal.displayInfo("Maya Scene Extractor loaded")

        # self.category_functions = {"model": self._extract_model,
        #                            "animation": self._extract_animation,
        #                            "fx": self._extract_fx}

    # def extract(self):
    #     func = self.category_functions.get(self.category, self._extract_default)
    #     pass

    def _extract_default(self):
        """Extract method for any non-specified category"""
        pass
        # extension = pathlib.Path(self.output_path).suffix
        # file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        # cmds.file(rename=self.output_path)
        # cmds.file(save=True, type=file_format)