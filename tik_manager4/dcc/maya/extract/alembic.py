"""Extract Alembic from Maya scene"""

from maya import cmds
from maya import OpenMaya as om

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.maya import utils



class Alembic(ExtractCore):
    """Extract Alembic from Maya scene."""
    name = "alembic"  # IMPORTANT. Must match to the one in category_definitions.json
    nice_name = "Alembic"
    color = (244, 132, 132)
    _ranges = utils.get_ranges()

    # these are the exposed settings in the UI
    default_settings = {
        "Animation": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
        },
        "Fx": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
        },
        "Layout": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
        "Lighting": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
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
                                   "Fx": self._extract_animation,
                                   "Layout": self._extract_layout,
                                   "Lighting": self._extract_layout,
                                   }


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
        _start_frame = settings.get_property("start_frame")
        _end_frame = settings.get_property("end_frame")
        step = float(1.0/settings.get_property("sub_steps"))
        _flags = f"-frameRange {_start_frame} {_end_frame} -step {step} -uvWrite -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa"
        command = f"{_flags} -file {_file_path}"
        cmds.AbcExport(j=command)

    def _extract_layout(self):
        """Extract method for fx category"""
        settings = self.settings.get("Layout", {})
        _file_path = self.resolve_output()
        _start_frame = settings.get_property("start_frame")
        _end_frame = settings.get_property("end_frame")
        _flags = f"-frameRange {_start_frame} {_end_frame} -step 1.0 -uvWrite -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa"
        command = f"{_flags} -file {_file_path}"
        cmds.AbcExport(j=command)

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        _flags = "-frameRange 0 0 -ro -uvWrite -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa"
        command = "{0} -file {1}".format(_flags, _file_path)
        cmds.AbcExport(j=command)
