"""Ingest source scene."""

import nuke
from tik_manager4.dcc.ingest_core import IngestCore


class Source(IngestCore):
    """Ingest Source Maya Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".mb", ".ma"]

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Maya scene."""
        nuke.tprint("Bringing in Source Scene")
        nuke.nodePaste(self.ingest_path)

    def _reference_default(self):
        """Reference the Maya scene."""

        # this method will be used for all categories
        nuke.tprint("Referencing Source Scene. (Identical to importing)")
        self._bring_in_default()
