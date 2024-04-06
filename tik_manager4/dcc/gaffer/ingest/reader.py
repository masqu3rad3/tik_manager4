"""Element reader for Gaffer ingest module"""

from pathlib import Path

import GafferScene

from tik_manager4.dcc.gaffer import gaffer_menu

from tik_manager4.dcc.ingest_core import IngestCore

class Reader(IngestCore):
    """Ingest elements."""

    nice_name = "Reader"
    valid_extensions = [".abc", ".lscc", ".scc", ".usd", ".usda", ".usdc", ".usdz", ".vdb"]
    referencable = False

    def __init__(self):
        super(Reader, self).__init__()
        self.gaffer = gaffer_menu.GafferMenu()
    def _bring_in_default(self):
        """Import various file types."""
        reader_node = GafferScene.SceneReader()
        self.gaffer.script.addChild(reader_node)
        reader_node["fileName"].setValue(Path(self.ingest_path).as_posix())