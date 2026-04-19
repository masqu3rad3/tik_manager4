"""Extract Psd file."""

from krita import Krita, InfoObject

from tik_manager4.dcc.extract_core import ExtractCore


class Psd(ExtractCore):
    """Extract Psd file"""

    nice_name = "PSD"
    color = (140, 15, 220)  # Bluish Purple

    def __init__(self):
        super(Psd, self).__init__()

        self.extension = ".psd"

    def _extract_default(self):
        """Extract Psd."""
        doc = Krita.instance().activeDocument()
        info = InfoObject()
        doc.exportImage(self.resolve_output(), info)
