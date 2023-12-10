"""Ingest Alembic."""

from pathlib import Path
from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.ingest_core import IngestCore

class Alembic(IngestCore):
    """Ingest Source Maya Scene."""
    name = "alembic"
    nice_name =  "Ingest Alembic"
    valid_extensions = [".abc"]

    def __init__(self):
        super(Alembic, self).__init__()
        if not cmds.pluginInfo("AbcImport", loaded=True, query=True):
            try:
                cmds.loadPlugin("AbcImport")
            except Exception as e:
                om.MGlobal.displayInfo("Alembic Import Plugin cannot be initialized")
                raise e

        self.category_functions = {"Model": self._bring_in_model,
                                   "Animation": self._bring_in_animation}

    def _bring_in_model(self, file_path):
        """Import Alembic File."""
        cmds.AbcImport(file_path, mode="import", fitTimeRange=False, setToStartFrame=False)

    def _bring_in_animation(self, file_path):
        """Import Alembic File."""
        cmds.AbcImport(file_path, mode="import", fitTimeRange=True, setToStartFrame=True)

    def _bring_in_default(self, file_path):
        """Import Alembic File."""
        cmds.AbcImport(file_path)

    def reference(self, file_path, namespace=None):
        """Create a GPU Cache for alembics instead of reference."""
        # Create Cache Node
        namespace = namespace or Path(file_path).stem
        cache_node = cmds.createNode("gpuCache", name=f"{namespace}Cache")
        cache_parent = cmds.listRelatives(cache_node, parent=True, path=True)
        cache_parent = cmds.rename(cache_parent, namespace)
        # Set Cache Path
        cmds.setAttr(f"{cache_node}.cacheFileName", file_path, type="string")
        # Namespace
        if not cmds.namespace(exists=namespace):
            cmds.namespace(addNamespace=namespace)
        # Apply Namespace
        cache_parent = cmds.rename(cache_parent, f"{namespace}:{cache_parent}")
        return cache_parent