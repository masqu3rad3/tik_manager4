"""Ingest Alembic."""

from pathlib import Path
import hou
from tik_manager4.dcc.ingest_core import IngestCore

class Alembic(IngestCore):
    """Ingest Alembic."""

    nice_name =  "Ingest Alembic"
    valid_extensions = [".abc"]

    def __init__(self):
        super(Alembic, self).__init__()

        # self.category_functions = {"Model": self._bring_in_model,
        #                            "Animation": self._bring_in_animation,
        #                            "Fx": self._bring_in_fx,
        #                            "Layout": self._bring_in_layout,
        #                            "Lighting": self._bring_in_lighting,
        #                            }

    def _bring_in_default(self):
        """Import Alembic File."""
        # get the project path
        project_path = hou.getenv("JOB")
        # try to get a relative path to the project. If it is not possible, use the absolute path.
        try: _file_path = "$JOB" / Path(self.file_path).relative_to(project_path)
        except ValueError: _file_path = Path(self.file_path)

        node = hou.node("obj")
        alembic_node = node.createNode("alembicarchive", node_name=_file_path.stem)
        alembic_node.moveToGoodPosition()
        alembic_node.parm("fileName").set(str(_file_path))

        alembic_node.parm("viewportlod").set("full")
        alembic_node.parm("flattenVisibility").set(True)
        alembic_node.parm("channelRef").set(False)
        alembic_node.parm("buildSingleGeoNode").set(False)
        alembic_node.parm("loadUserProps").set("none")
        alembic_node.parm("loadmode").set("houdini")
        alembic_node.parm("buildSubnet").set(False)

        alembic_node.parm("buildHierarchy").pressButton()

            # relative_path = Path(self.file_path).relative_to(self.project_path)

    #     om.MGlobal.displayInfo("Bringing in Alembic Model")
    #     cmds.AbcImport(self.file_path, mode="import", fitTimeRange=False, setToStartFrame=False)
    #
    # def _bring_in_animation(self):
    #     """Import Alembic File."""
    #     om.MGlobal.displayInfo("Bringing in Alembic Animation")
    #     cmds.AbcImport(self.file_path, mode="import", fitTimeRange=True, setToStartFrame=True)
    #
    # def _bring_in_fx(self):
    #     """Import Alembic File."""
    #     om.MGlobal.displayInfo("Bringing in Alembic FX")
    #     # identical to animation
    #     self._bring_in_animation()
    #
    # def _bring_in_layout(self):
    #     """Import Alembic File."""
    #     om.MGlobal.displayInfo("Bringing in Alembic Layout")
    #     # identical to animation
    #     self._bring_in_animation()
    #
    # def _bring_in_lighting(self):
    #     """Import Alembic File."""
    #     om.MGlobal.displayInfo("Bringing in Alembic Lighting")
    #     # identical to animation
    #     self._bring_in_animation()
    #
    # def _bring_in_default(self):
    #     """Import Alembic File."""
    #     om.MGlobal.displayInfo("Bringing in Alembic with default settings")
    #     cmds.AbcImport(self.file_path)
    #
    # def _reference_default(self):
    #     """Create a GPU Cache for alembics instead of reference."""
    #
    #     # this method will be used for all categories
    #     # Create Cache Node
    #     namespace = self.namespace or Path(self.file_path).stem
    #     cache_node = cmds.createNode("gpuCache", name=f"{namespace}Cache")
    #     cache_parent = cmds.listRelatives(cache_node, parent=True, path=True)
    #     cache_parent = cmds.rename(cache_parent, namespace)
    #     # Set Cache Path
    #     cmds.setAttr(f"{cache_node}.cacheFileName", self.file_path, type="string")
    #     # Namespace
    #     if not cmds.namespace(exists=namespace):
    #         cmds.namespace(addNamespace=namespace)
    #     # Apply Namespace
    #     cache_parent = cmds.rename(cache_parent, f"{namespace}:{cache_parent}")
    #     return cache_parent