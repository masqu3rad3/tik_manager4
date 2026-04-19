"""Ingest PSD."""

from krita import Krita

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.krita import utils


class Image(IngestCore):
    """Ingest Psd file."""

    nice_name = "Ingest PSD"
    valid_extensions = [".psd"]
    referencable = False

    def _bring_in_default(self):
        """Import the image."""
        utils.open_image_file(self.ingest_path)
