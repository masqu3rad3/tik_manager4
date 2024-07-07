"""Ingest STL to 3ds Max Scene."""

from pathlib import Path

from pymxs import runtime as rt

from tik_manager4.dcc.ingest_core import IngestCore


class Stl(IngestCore):
    """Ingest STL to 3ds Max Scene."""
    nice_name = "Ingest STL"
    valid_extensions = [".stl"]
    referencable = False

    def __init__(self):
        super(Stl, self).__init__()

    def _bring_in_default(self):
        """Import STL File."""
        rt.importFile(self.ingest_path, rt.Name("NoPrompt"), using=rt.STL_Import)