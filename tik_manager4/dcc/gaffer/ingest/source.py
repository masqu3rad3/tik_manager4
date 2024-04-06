"""Ingest source scenne."""

from tik_manager4.dcc.gaffer import gaffer_menu

from tik_manager4.dcc.ingest_core import IngestCore

class Source(IngestCore):
    """Ingest Source Gaffer Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".gfr"]
    referencable = False

    def __init__(self):
        super(Source, self).__init__()
        self.gaffer = gaffer_menu.GafferMenu()

    def _bring_in_default(self):
        """Import the Gaffer scene."""
        self.gaffer.script.importFile(self.ingest_path)

