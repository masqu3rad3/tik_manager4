"""Ingest FBX."""

from pathlib import Path
from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.maya import fbx_utility as fbxu
from tik_manager4.dcc.ingest_core import IngestCore

class Alembic(IngestCore):
    """Ingest Source Maya Scene."""
    name = "fbx"
    nice_name =  "Ingest fbx"
    valid_extensions = [".fbx"]

    def __init__(self):
        super().__init__()
        if not cmds.pluginInfo("fbxmaya", loaded=True, query=True):
            try:
                cmds.loadPlugin("fbxmaya")
            except Exception as e:
                om.MGlobal.displayInfo("FBX Plugin cannot be initialized")
                raise e

        self.category_functions = {"Model": self._bring_in_default,
                                   "Animation": self._bring_in_default}

    def _bring_in_model(self, file_path):
        """Import FBX file."""
        fbxu.load(file_path, merge_mode="add", animation=False)

    def _bring_in_animation(self, file_path):
        """Import FBX file."""
        fbxu.load(file_path, merge_mode="merge", animation=True)

    def _bring_in_default(self, file_path):
        """Import FBX file."""
        fbxu.load(file_path)

    def reference(self, file_path, namespace=None):
        """Create a GPU Cache for alembics instead of reference."""
        # Create Cache Node
        ref = cmds.file(
            file_path,
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=namespace,
            returnNewNodes=True,
        )
        return ref