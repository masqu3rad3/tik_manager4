"""Ingest Alembic."""

from pathlib import Path
from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.ingest_core import IngestCore

class Alembic(IngestCore):
    """Ingest Alembic."""
    name = "alembic"
    nice_name =  "Ingest Alembic"
    valid_extensions = [".abc"]

    def __init__(self):
        super(Alembic, self).__init__()
        if not cmds.pluginInfo("AbcImport", loaded=True, query=True):
            try:
                cmds.loadPlugin("AbcImport")
            except Exception as exc:
                om.MGlobal.displayInfo("Alembic Import Plugin cannot be initialized")
                raise exc

        self.category_functions = {"Model": self._bring_in_model,
                                   "Animation": self._bring_in_animation,
                                   "Fx": self._bring_in_fx,
                                   "Layout": self._bring_in_layout,
                                   "Lighting": self._bring_in_lighting,
                                   }

    def _bring_in_model(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Model")
        cmds.AbcImport(self.file_path, mode="import", fitTimeRange=False, setToStartFrame=False)

    def _bring_in_animation(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Animation")
        cmds.AbcImport(self.file_path, mode="import", fitTimeRange=True, setToStartFrame=True)

    def _bring_in_fx(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic FX")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_layout(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Layout")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_lighting(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Lighting")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_default(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic with default settings")
        cmds.AbcImport(self.file_path)

    def _reference_default(self):
        """Create a GPU Cache for alembics instead of reference."""

        # this method will be used for all categories
        # Create Cache Node
        namespace = self.namespace or Path(self.file_path).stem
        cache_node = cmds.createNode("gpuCache", name=f"{namespace}Cache")
        cache_parent = cmds.listRelatives(cache_node, parent=True, path=True)
        cache_parent = cmds.rename(cache_parent, namespace)
        # Set Cache Path
        cmds.setAttr(f"{cache_node}.cacheFileName", self.file_path, type="string")
        # Namespace
        if not cmds.namespace(exists=namespace):
            cmds.namespace(addNamespace=namespace)
        # Apply Namespace
        cache_parent = cmds.rename(cache_parent, f"{namespace}:{cache_parent}")
        return cache_parent