"""Extract Alembic from Maya scene"""

from maya import cmds
from maya import OpenMaya as om

from tik_manager4.core import settings
from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.maya import utils
from tik_manager4.core.settings import Settings



class Alembic(ExtractCore):
    """Extract Alembic from Maya scene."""
    name = "alembic"  # IMPORTANT. Must match to the one in category_definitions.json
    nice_name = "Alembic"
    color = (244, 132, 132)
    _ranges = utils.get_ranges()
    default_settings = {
        "Animation": {
            "frame_range": [_ranges[0], _ranges[3]],
            "step": 1.0
        }
    }
    def __init__(self):
        super().__init__()
        if not cmds.pluginInfo("AbcExport", loaded=True, query=True):
            try:
                cmds.loadPlugin("AbcExport")
            except Exception as e:  # pylint: disable=broad-except
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
        _flags = "-frameRange 0 0 -ro -uvWrite -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa"
        command = "{0} -file {1}".format(_flags, _file_path)
        cmds.AbcExport(j=command)

    def _extract_animation(self):
        """Extract method for animation category"""
        settings = self.settings.get("Animation", {})
        _file_path = self.resolve_output()
        frame_range = settings.get_property("frame_range")
        step = settings.get_property("step")
        _flags = f"-frameRange {frame_range[0]} {frame_range[1]} -step {step} -uvWrite -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa"
        command = f"{_flags} -file {_file_path}"
        cmds.AbcExport(j=command)


    def _extract_fx(self):
        """Extract method for fx category"""
        settings = self.settings.get("Animation", {})
        _file_path = self.resolve_output()
        range_start = settings["frame_range"][0]
        range_end = settings["frame_range"][1]
        step = settings["step"]
        _flags = f"-frameRange {range_start} {range_end} -step {step} -uvWrite -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa"
        command = f"{_flags} -file {_file_path}"
        cmds.AbcExport(j=command)

    def _extract_default(self):
        """Extract method for any non-specified category"""
        om.MGlobal.displayWarning("Default category is not implemented yet")
        pass
