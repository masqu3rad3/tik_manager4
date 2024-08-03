"""Extract Nuke scene."""
from pathlib import Path

import nuke
from tik_manager4.dcc.extract_core import ExtractCore

# The Collector will only collect classes inherit ExtractCore
class Source(ExtractCore):
    """Extract Source Nuke scene"""

    nice_name = "Source Scene"
    color = (255, 255, 255)

    def __init__(self):
        super().__init__()
        nuke.tprint("Nuke Scene Extractor loaded")

        # we will keep the original extension. This will be updated in the _extract_default method.
        self.extension = ""

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        # get the extension from the current nuke script.
        self.extension = Path(nuke.root().name()).suffix
        _file_path = Path(_file_path).with_suffix(self.extension)
        nuke.scriptSave(_file_path.as_posix())
