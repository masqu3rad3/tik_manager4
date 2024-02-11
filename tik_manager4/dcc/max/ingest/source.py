"""Ingest source scene."""

import pymxs
from pymxs import runtime as rt
from tik_manager4.dcc.ingest_core import IngestCore


class Source(IngestCore):
    """Ingest Source Maya Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".max"]
    referenceable = True

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Maya scene."""
        rt.mergeMaxFile(self.ingest_path, prompt=False)

    def _reference_default(self):
        """Reference the Maya scene."""
        # this method will be used for all categories
        xrefobjs = rt.getMAXFileObjectNames(self.ingest_path)
        rt.xrefs.addNewXRefObject(self.ingest_path, xrefobjs)

