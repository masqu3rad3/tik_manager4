"""Ingest Alembic."""

from pathlib import Path
import hou
from tik_manager4.dcc.ingest_core import IngestCore

class Alembic(IngestCore):
    """Ingest Alembic."""

    nice_name =  "Ingest Alembic"
    valid_extensions = [".abc"]
    referenceable = False

    def __init__(self):
        super(Alembic, self).__init__()

    def _bring_in_default(self):
        """Import Alembic File.
        This method is used for all categories where no specific method is defined.
        """
        # get the project path
        project_path = hou.getenv("JOB")
        # try to get a relative path to the project. If it is not possible, use the absolute path.
        try: _file_path = "$JOB" / Path(self.ingest_path).relative_to(project_path)
        except ValueError: _file_path = Path(self.ingest_path)

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

    def _reference_default(self):
        """Reference Alembic File."""
        # identical to bring in
        self._bring_in_default()