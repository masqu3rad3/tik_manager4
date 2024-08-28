"""Ingest Usd."""

from pathlib import Path
import hou
from tik_manager4.dcc.ingest_core import IngestCore

import logging

LOG = logging.getLogger(__name__)


class Usd(IngestCore):
    """Ingest Usd."""

    nice_name = "Ingest Usd"
    valid_extensions = [".usd", ".usda", ".usdc", ".usdz", ".usdnc"]
    referencable = True

    def __init__(self):
        super(Usd, self).__init__()

    def _bring_in_default(self):
        """Import USD File.
        This method is used for all categories where no specific method is defined.
        """
        # get the project path
        project_path = hou.getenv("JOB")
        # try to get a relative path to the project. If it is not possible, use the absolute path.
        try:
            _file_path = "$JOB" / Path(self.ingest_path).relative_to(project_path)
        except ValueError:
            _file_path = Path(self.ingest_path)

        node = hou.node("obj")
        geo_node = node.createNode("geo", node_name=_file_path.stem)
        # this is to delete any existing nodes in the geo node
        try:
            geo_node.allSubChildren()[0].destroy()
        except IndexError:
            pass
        geo_node.moveToGoodPosition()

        usd_import_node = geo_node.createNode("usdimport", node_name=_file_path.stem)
        usd_import_node.moveToGoodPosition()
        usd_import_node.parm("filepath1").set(str(_file_path))

    def _reference_default(self):
        """Reference Usd File."""
        # staget the USD
        # Get the Solaris network path (LOP network)
        lopnet_path = "/stage"
        lopnet = hou.node(lopnet_path)
        if lopnet is None:
            # If the Solaris network doesn't exist, create one
            lopnet = hou.node("/").createNode("lopnet", "stage")

        # Create a 'reference' node in Solaris
        reference_node = lopnet.createNode("reference")
        # rename it as the file name
        # reference_node.setName(Path(self.ingest_path).stem)
        if self.namespace:
            reference_node.setName(self.namespace)
        reference_node.moveToGoodPosition()
        # try to get a relative path to the project. If it is not possible, use the absolute path.
        project_path = hou.getenv("JOB")
        try:
            _file_path = "$JOB" / Path(self.ingest_path).relative_to(project_path)
        except ValueError:
            _file_path = Path(self.ingest_path)
        # Set the path to the reference file
        reference_node.parm("filepath1").set(_file_path.as_posix())
