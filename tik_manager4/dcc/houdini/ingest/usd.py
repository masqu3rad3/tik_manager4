"""Ingest Usd."""

from pathlib import Path
import hou
from tik_manager4.dcc.ingest_core import IngestCore

class Usd(IngestCore):
    """Ingest Usd."""

    nice_name =  "Ingest Usd"
    valid_extensions = [".usd", ".usda", ".usdc", ".usdz", ".usdnc"]
    referencable = False

    def __init__(self):
        super(Usd, self).__init__()

    def _bring_in_default(self):
        """Import USD File.
        This method is used for all categories where no specific method is defined.
        """
        # get the project path
        project_path = hou.getenv("JOB")
        # try to get a relative path to the project. If it is not possible, use the absolute path.
        try: _file_path = "$JOB" / Path(self.ingest_path).relative_to(project_path)
        except ValueError: _file_path = Path(self.ingest_path)

        node = hou.node("obj")
        geo_node = node.createNode("geo", node_name=_file_path.stem)
        # this is to delete any existing nodes in the geo node
        try: geo_node.allSubChildren()[0].destroy()
        except IndexError: pass
        geo_node.moveToGoodPosition()

        usd_import_node = geo_node.createNode("usdimport", node_name=_file_path.stem)
        usd_import_node.moveToGoodPosition()
        usd_import_node.parm("filepath1").set(str(_file_path))

    def _reference_default(self):
        """Reference Usd File."""
        # identical to bring in
        self._bring_in_default()