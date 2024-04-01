"""Ingest Usd."""

from Katana import NodegraphAPI
from tik_manager4.dcc.ingest_core import IngestCore

# Specify the filename for the USD file
usd_filename = "/path/to/your/usd/file.usd"

# Create the USDIn node
usd_in_node = NodegraphAPI.CreateNode("UsdIn", NodegraphAPI.GetRootNode())

# Set the filename parameter of the USDIn node
usd_in_node.getParameter("fileName").setValue(usd_filename, 0)


class Usd(IngestCore):
    """Ingest Usd."""

    nice_name =  "Ingest Usd"
    valid_extensions = [".usd", ".usda", ".usdc", ".usdz"]
    referencable = False

    def _bring_in_default(self):
        """Import Usd File."""
        usd_in_node = NodegraphAPI.CreateNode("UsdIn", NodegraphAPI.GetRootNode())
        usd_in_node.getParameter("fileName").setValue(self.ingest_path, 0)