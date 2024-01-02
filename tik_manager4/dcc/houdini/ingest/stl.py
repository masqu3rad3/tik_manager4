"""Ingest STL."""

from pathlib import Path

import hou

from tik_manager4.dcc.ingest_core import IngestCore


class Stl(IngestCore):
    """Ingest STL."""
    nice_name = "Ingest STL"
    valid_extensions = [".stl"]

    def __init__(self):
        super(Stl, self).__init__()
        self._bunlded = True

    def _bring_in_default(self):
        """Import STL File."""
        stl_files = [file for file in Path(self.ingest_path).glob("*") if file.suffix.lower() in self.valid_extensions]
