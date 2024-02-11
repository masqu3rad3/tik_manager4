"""Extract Katana Scene."""

from Katana import NodegraphAPI  # pylint: disable=import-error
from tik_manager4.dcc.extract_core import ExtractCore

class Source(ExtractCore):
    """Extract Source Katana scene"""

    nice_name = "Source Scene"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()

        self.extension = ".katana"

    def _extract_default(self):
        """Extract for any non-specified category."""
        file_path = self.resolve_output()
        element = NodegraphAPI.BuildNodegraphXmlIO(opaqueParams={})
        NodegraphAPI.WriteKatanaFile(file_path, element)

