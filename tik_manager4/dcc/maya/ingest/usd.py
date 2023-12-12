"""Ingest USD."""

from pathlib import Path
from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.ingest_core import IngestCore

class USD(IngestCore):
    """Ingest USD."""
    name = "usd"
    nice_name =  "Ingest USD"
    valid_extensions = [".usd", ".usda", ".usdc"]

    def __init__(self):
        super(USD, self).__init__()
        if not cmds.pluginInfo("mayaUsdPlugin", loaded=True, query=True):
            try:
                cmds.loadPlugin("mayaUsdPlugin")
            except Exception as exc:
                om.MGlobal.displayInfo("mayaUsdPlugin cannot be initialized")
                raise exc

        self.category_functions = {"Model": self._bring_in_model,
                                   "Animation": self._bring_in_animation}

    def _bring_in_model(self, file_path):
        """Import USD File."""
        cmds.mayaUSDImport(file_path, shadingMode="none")