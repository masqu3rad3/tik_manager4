"""Extract Svg file."""

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.krita import utils


class Svg(ExtractCore):
    """Extract Svg file"""

    nice_name = "SVG"
    color = (180, 15, 180)  # Magenta Purple

    def __init__(self):
        super(Svg, self).__init__()

        self.extension = ".svg"

    def _extract_default(self):
        """Extract Svg file."""
        utils.export_merged_visible_layers(self.resolve_output())
