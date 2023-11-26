"""Extract Maya scene."""

import pathlib
from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.extract_core import ExtractCore

# The Collector will only collect classes inherit ExtractCore
class Source(ExtractCore):
    """Extract Alembic from Maya scene"""
    name = "source" # IMPORTANT. Must match to the one in category_definitions.json
    nice_name = "Source Scene"
    color = (255, 255, 255)
    def __init__(self):
        super(Source, self).__init__()
        om.MGlobal.displayInfo("Maya Scene Extractor loaded")

        self.extension = ".mb"


    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        # file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        _original_path = cmds.file(query=True, sceneName=True)
        cmds.file(rename=_file_path)
        cmds.file(save=True, type="mayaBinary")
        cmds.file(rename=_original_path)