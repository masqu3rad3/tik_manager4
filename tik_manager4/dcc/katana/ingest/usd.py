"""Ingest Usd."""

from Katana import NodegraphAPI
from tik_manager4.dcc.ingest_core import IngestCore

class Usd(IngestCore):
    """Ingest Usd."""

    nice_name =  "Ingest Usd"
    valid_extensions = [".usd", ".usda", ".usdc", ".usdz"]
    referencable = False

    def _bring_in_default(self):
        """Import Usd File."""
        usd_in_node = NodegraphAPI.CreateNode("UsdIn", NodegraphAPI.GetRootNode())
        usd_in_node.getParameter("fileName").setValue(self.ingest_path, 0)