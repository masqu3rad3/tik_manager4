"""Extract Maya scene."""

import logging

from pathlib import Path
import shutil

import hou
from tik_manager4.dcc.extract_core import ExtractCore

LOG = logging.getLogger(__name__)

# The Collector will only collect classes inherit ExtractCore
class Source(ExtractCore):
    """Extract Source Maya scene"""

    nice_name = "Source Scene"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()
        # LOG.info("Houdini Scene Extractor loaded")

        # we will keep the original extension. This will be updated in the _extract_default method.
        self.extension = ""

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()  # this won't have an extension.
        # first save the file as a temporary backup file:
        _temp_backup = hou.hipFile.saveAsBackup()
        self.extension = Path(_temp_backup).suffix
        _file_path = Path(_file_path).with_suffix(self.extension)
        shutil.move(_temp_backup, _file_path)
