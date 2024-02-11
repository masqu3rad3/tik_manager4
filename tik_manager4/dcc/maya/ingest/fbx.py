"""Ingest FBX."""

from pathlib import Path
from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.maya import fbx_utility as fbxu
from tik_manager4.dcc.ingest_core import IngestCore


class Fbx(IngestCore):
    """Ingest Source Maya Scene."""

    nice_name = "Ingest fbx"
    valid_extensions = [".fbx"]
    referenceable = True

    def __init__(self):
        super().__init__()
        if not cmds.pluginInfo("fbxmaya", loaded=True, query=True):
            try:
                cmds.loadPlugin("fbxmaya")
            except Exception as e:
                om.MGlobal.displayInfo("FBX Plugin cannot be initialized")
                raise e

        self.category_functions = {
            "Model": self._bring_in_model,
            "Rig": self._bring_in_default,
            "Layout": self._bring_in_layout,
            "Animation": self._bring_in_animation,
            "Fx": self._bring_in_fx,
            "Lighting": self._bring_in_lighting,
        }

    def _bring_in_model(self):
        """Import FBX file."""
        om.MGlobal.displayInfo("Bringing in FBX Model")
        fbxu.load(self.ingest_path, merge_mode="add", animation=False)

    def _bring_in_animation(self):
        """Import FBX file."""
        om.MGlobal.displayInfo("Bringing in FBX Animation")
        fbxu.load(self.ingest_path, merge_mode="merge", animation=True)

    def _bring_in_layout(self):
        """Import FBX file."""
        om.MGlobal.displayInfo("Bringing in FBX Layout")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_fx(self):
        """Import FBX file."""
        om.MGlobal.displayInfo("Bringing in FBX FX")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_lighting(self):
        """Import FBX file."""
        om.MGlobal.displayInfo("Bringing in FBX Lighting")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_default(self):
        """Import FBX file."""
        om.MGlobal.displayInfo("Bringing in FBX with default settings")
        fbxu.load(self.ingest_path)

    def _reference_default(self):
        """Reference the FBX file."""

        # this method will be used for all categories
        namespace = self.namespace or Path(self.ingest_path).stem
        ref = cmds.file(
            self.ingest_path,
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=namespace,
            returnNewNodes=True,
        )
        return ref
