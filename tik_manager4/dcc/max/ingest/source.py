"""Ingest source scene."""

from pathlib import Path

import pymxs
from pymxs import runtime as rt
from tik_manager4.dcc.ingest_core import IngestCore


class Source(IngestCore):
    """Ingest Source Maya Scene."""

    name = "source"
    nice_name = "Ingest Source Scene"
    valid_extensions = [".max"]

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Maya scene."""
        pymxs.print_("Bringing in Source Scene")
        rt.mergeMaxFile(self.file_path, prompt=False)

    def _reference_default(self):
        """Reference the Maya scene."""
        # this method will be used for all categories
        pymxs.print_("Referencing Source Scene")
        xrefobjs = rt.getMAXFileObjectNames(self.file_path)
        rt.xrefs.addNewXRefObject(self.file_path, xrefobjs)

