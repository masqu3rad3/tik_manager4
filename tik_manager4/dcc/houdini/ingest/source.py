"""Ingest source scene."""

import logging

import hou
from tik_manager4.dcc.ingest_core import IngestCore

LOG = logging.getLogger(__name__)

class Source(IngestCore):
    """Ingest Source Maya Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".hipnc", ".hiplc", ".hip"]

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Maya scene."""
        # LOG.info("Bringing in Source Scene")
        hou.hipFile.merge(self.file_path, node_pattern="*", overwrite_on_conflict=False, ignore_load_warnings=False)

    def _reference_default(self):
        """Reference the Maya scene."""

        # this method will be used for all categories
        # LOG.info("Bringing in Source Scene (No referencing in Houdini")
        self._bring_in_default()
