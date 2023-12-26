"""Ingest USD."""

from pathlib import Path

import logging

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.ingest_core import IngestCore

LOG = logging.getLogger(__name__)

class USD(IngestCore):
    """Ingest USD."""

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
                                   "LookDev": self._bring_in_lookdev,
                                   "Assembly": self._bring_in_assembly,
                                   "Layout": self._bring_in_layout,
                                   "Animation": self._bring_in_animation,
                                   "Fx": self._bring_in_fx,
                                   "Lighting": self._bring_in_lighting,
                                   }

    def _bring_in_default(self):
        """Import USD File with default settings."""
        cmds.mayaUSDImport(file=self.file_path, primPath="/")

    def _bring_in_model(self):
        """Import USD File for model category."""
        cmds.mayaUSDImport(file=self.file_path, readAnimData=False, useAsAnimationCache=False, primPath="/")

    def _bring_in_lookdev(self):
        """Import USD File for lookdev category."""
        # identical to model
        self._bring_in_model()

    def _bring_in_assembly(self):
        """Import USD File for assembly category."""
        # identical to model
        self._bring_in_model()

    def _bring_in_layout(self):
        """Import USD File for layout category."""
        # identical to animation
        self._bring_in_animation()

    def _bring_in_animation(self):
        """Import USD File."""
        cmds.mayaUSDImport(file=self.file_path, readAnimData=1, useAsAnimationCache=True, primPath="/")

    def _bring_in_fx(self):
        """Import USD File."""
        # identical to animation
        self._bring_in_animation()

    def _bring_in_lighting(self):
        """Import USD File."""
        # identical to animation
        self._bring_in_animation()

    def _reference_default(self):
        """Reference USD File with default settings."""

        # this method will be used for all categories
        namespace = self.namespace or Path(self.file_path).stem
        ref = cmds.file(
            self.file_path,
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=namespace,
            returnNewNodes=True,
        )
        return ref
