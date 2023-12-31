"""Extract STL from Maya Scene"""

from maya import cmds
from maya import OpenMaya as om

from tik_manager4.dcc.extract_core import ExtractCore


class Stl(ExtractCore):
    """Extract STL from Maya scene."""

    nice_name = "STL"
    color = (100, 200, 0)

    def __init__(self):
        super().__init__()
        if not cmds.pluginInfo("stlTranslator", loaded=True, query=True):
            try:
                cmds.loadPlugin("stlTranslator")
            except Exception as e:
                om.MGlobal.displayInfo("STL Plugin cannot be initialized")
                raise e

        om.MGlobal.displayInfo("STL Extractor loaded")

        self._extension = ".stl"
        # we don't need to define category functions for STL

    def _extract_default(self):
        """Extract STL from Maya scene."""
        # STL files are not supporting ranges. For our purposes we will
        # use the same _extract_default function for all categories.

        _file_path = self._get_file_path()
        cmds.file(_file_path, force=True, options="v=0;", typ="stl", exportSelected=False)