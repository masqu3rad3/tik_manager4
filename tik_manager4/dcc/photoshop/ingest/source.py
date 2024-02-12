"""Ingest Source Photoshop Scene."""

from win32com.client import Dispatch

from tik_manager4.dcc.ingest_core import IngestCore

class Source(IngestCore):
    """Ingest Source Photoshop Scene."""

    nice_name = "Ingest Source Photoshop Scene"
    valid_extensions = [".psd", ".psb"]
    referenceable = False

    def __init__(self):
        super(Source, self).__init__()

        self.com_link = Dispatch("Photoshop.Application")

    def _bring_in_default(self):
        """Import the Photoshop scene."""
        self.com_link.Open(self.ingest_path)

    def _reference_default(self):
        """Reference the Photoshop scene. This is same as bring in. (Open)"""
        # this method will be used for all categories
        self._bring_in_default()
