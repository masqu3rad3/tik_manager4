"""Ingest image."""

from krita import Krita

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.krita import utils


class Image(IngestCore):
    """Ingest image."""

    nice_name = "Ingest Image"
    valid_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".exr", ".tga"]
    referencable = False

    def _bring_in_default(self):
        """Import the image."""
        utils.open_image_file(self.ingest_path)
