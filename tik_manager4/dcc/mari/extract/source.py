"""Archive the Mari Project."""

import mari

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.mari import utils


class Source(ExtractCore):
    """Archive the Mari Project."""

    nice_name = "Mri Backup"
    color = (255, 255, 255)
    def __init__(self):
        super(Source, self).__init__()

        self.extension = ".mri"

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        utils.save_as(_file_path)
