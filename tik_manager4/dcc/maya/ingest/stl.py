"""Ingest STL."""

from pathlib import Path

from maya import cmds
from maya import OpenMaya as om

from tik_manager4.dcc.ingest_core import IngestCore


class Stl(IngestCore):
    """Ingest STL."""

    nice_name = "Ingest STL"
    valid_extensions = [".stl"]
    bundled = True
    referencable = False

    def __init__(self):
        super().__init__()
        if not cmds.pluginInfo("stlTranslator", loaded=True, query=True):
            try:
                cmds.loadPlugin("stlTranslator")
            except Exception as exc:
                om.MGlobal.displayInfo("STL Import Plugin cannot be initialized")
                raise exc

    def _bring_in_default(self):
        """Import STL File."""
        om.MGlobal.displayInfo("Bringing in STL with default settings")
        # get all the files in the bundle directory matching the valid extensions.
        # we will import all of them
        all_files = list(Path(self.ingest_path).glob("*"))
        stl_files = [file for file in all_files if file.suffix.lower() in self.valid_extensions]
        for stl_file in stl_files:
            # Global import settings
            cmds.file(stl_file, i=True, type="STLImport")
