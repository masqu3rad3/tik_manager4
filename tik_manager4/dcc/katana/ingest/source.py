"""Ingest Source Katana Scene."""

from Katana import KatanaFile  # pylint: disable=import-error
from tik_manager4.dcc.ingest_core import IngestCore


class Source(IngestCore):
    """Ingest Source Katana Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".katana"]
    referencable = False

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Katana scene."""
        KatanaFile.Import(self.ingest_path)

    def _reference_default(self):
        """Reference the Katana scene."""
        self._bring_in_default()