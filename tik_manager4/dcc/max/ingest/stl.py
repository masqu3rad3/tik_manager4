"""Ingest STL to 3ds Max Scene."""

from pathlib import Path

from pymxs import runtime as rt

from tik_manager4.dcc.ingest_core import IngestCore


class Stl(IngestCore):
    """Ingest STL to 3ds Max Scene."""
    nice_name = "Ingest STL"
    valid_extensions = [".stl"]
    bundled = True
    referencable = False

    def __init__(self):
        super(Stl, self).__init__()

    def _bring_in_default(self):
        all_files = list(Path(self.ingest_path).glob("*"))
        stl_files = [file for file in all_files if file.suffix.lower() in self.valid_extensions]
        for stl_file in stl_files:
            rt.importFile(stl_file.as_posix(), rt.Name("NoPrompt"), using=rt.STL_Import)