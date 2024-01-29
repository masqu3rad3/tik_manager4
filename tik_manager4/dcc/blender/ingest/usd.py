"""Ingest Usd."""

import bpy
from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.blender import utils

class Usd(IngestCore):
    """Ingest Usd."""

    nice_name = "Ingest Usd"
    valid_extensions = [".usd", ".usda", ".usdc", ".usdz"]

    def __init__(self):
        super(Usd, self).__init__()

    def _bring_in_default(self):
        """Import Alembic File.
        This method is used for all categories where no specific method is defined.
        """
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.usd_import(filepath=self.ingest_path, import_usd_preview=True)

    def _reference_default(self):
        """Reference Usd File."""
        # identical to bring in
        self._bring_in_default()