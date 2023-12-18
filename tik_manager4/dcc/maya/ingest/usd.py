"""Ingest USD."""

import logging

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.ingest_core import IngestCore

LOG = logging.getLogger(__name__)

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
                                   "Animation": self._bring_in_animation,
                                   "Fx": self._bring_in_fx,
                                   "LookDev": self._bring_in_lookdev,
                                   "Layout": self._bring_in_layout,
                                   "Assembly": self._bring_in_assembly,
                                   }

    def _bring_in_model(self, file_path):
        """Import USD File."""
        LOG.warning("USD importer for model category is not implemented yet.")

    def _bring_in_animation(self, file_path):
        """Import USD File."""
        LOG.warning("USD importer for animation category is not implemented yet.")

    def _bring_in_fx(self, file_path):
        """Import USD File."""
        LOG.warning("USD importer for fx category is not implemented yet.")