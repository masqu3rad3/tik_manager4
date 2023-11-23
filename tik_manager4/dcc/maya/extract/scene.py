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
        super(Scene, self).__init__()
        om.MGlobal.displayInfo("Maya Scene Extractor loaded")

        self.extension = ".mb"
        # self.category_functions = {"model": self._extract_model,
        #                            "animation": self._extract_animation,
        #                            "fx": self._extract_fx}

    # def extract(self):
    #     func = self.category_functions.get(self.category, self._extract_default)
    #     pass

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        # file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        _original_path = cmds.file(query=True, sceneName=True)
        cmds.file(rename=_file_path)
        cmds.file(save=True, type="mayaBinary")
        cmds.file(rename=_original_path)