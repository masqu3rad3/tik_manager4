"""Ingest Source Krita Scene."""

from krita import Krita

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.krita import utils


class Source(IngestCore):
    """Ingest Source Krita Scene."""

    nice_name = "Ingest Source  Scene"
    valid_extensions = [".kra"]
    referencable = False

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Krita scene."""
        utils.open_image_file(self.ingest_path)

    def _reference_default(self):
        """Reference the Krita scene. This is same as bring in. (Open)"""
        # this method will be used for all categories
        self._bring_in_default()
