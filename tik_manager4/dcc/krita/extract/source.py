"""Extract Krita Scene."""

from krita import Krita

from tik_manager4.dcc.extract_core import ExtractCore


class Source(ExtractCore):
    """Extract Source Krita scene"""

    nice_name = "Source Scene"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()

        self.extension = ".kra"

    def _extract_default(self):
        """Extract for any non-specified category."""
        Krita.instance().activeDocument().saveAs(self.resolve_output())
