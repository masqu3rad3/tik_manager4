"""Extract Alembic from Maya scene"""

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.extract_core import ExtractCore

# The Collector will only collect classes inherit ExtractCore
class Alembic(ExtractCore):
    """Extract Alembic from Maya scene"""
    name = "alembic" # IMPORTANT. Must match to the one in category_definitions.json
    def __init__(self):
        super(Alembic, self).__init__()
        if not cmds.pluginInfo("AbcExport", loaded=True, query=True):
            try:
                cmds.loadPlugin("AbcExport")
            except Exception as e:
                om.MGlobal.displayInfo("Alembic Plugin cannot be initialized")
                raise e

        om.MGlobal.displayInfo("Alembic Extractor loaded")

        self._extension = ".abc"
        # Category names must match to the ones in category_definitions.json (case sensitive)
        self.category_functions = {"Model": self._extract_model,
                                   "Animation": self._extract_animation,
                                   "Fx": self._extract_fx}

    def _extract_model(self):
        """Extract method for model category"""
        _file_path = self.resolve_output()
        _flags = "-frameRange 0 0 -ro -uvWrite -worldSpace -writeUVSets -writeVisibility -dataFormat ogawa"
        command = "{0} -file {1}".format(_flags, _file_path)
        cmds.AbcExport(j=command)

    def _extract_animation(self):
        """Extract method for animation category"""
        pass

    def _extract_fx(self):
        """Extract method for fx category"""
        pass

    def _extract_default(self):
        """Extract method for any non-specified category"""
        pass
