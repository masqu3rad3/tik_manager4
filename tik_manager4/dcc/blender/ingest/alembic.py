"""Ingest Alembic."""

import bpy

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.blender import utils


class Alembic(IngestCore):
    """Ingest Alembic."""

    nice_name = "Ingest Alembic"
    valid_extensions = [".abc"]

    def __init__(self):
        super(Alembic, self).__init__()

        self.category_functions = {"Model": self._bring_in_model,
                                   "Animation": self._bring_in_animation,
                                   "Fx": self._bring_in_fx,
                                   "Layout": self._bring_in_layout,
                                   "Lighting": self._bring_in_lighting,
                                   }

    def _bring_in_default(self):
        """Import Alembic File."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.alembic_import(filepath=self.ingest_path, set_frame_range=False)

    def _bring_in_model(self):
        """Import Alembic File."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.alembic_import(filepath=self.ingest_path, set_frame_range=False)

    def _bring_in_animation(self):
        """Import Alembic File."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.alembic_import(filepath=self.ingest_path, set_frame_range=True)

    def _bring_in_fx(self):
        """Import Alembic File."""
        self._bring_in_animation()

    def _bring_in_layout(self):
        """Import Alembic File."""
        self._bring_in_animation()

    def _bring_in_lighting(self):
        """Import Alembic File."""
        self._bring_in_animation()

    def _reference_default(self):
        """Reference Usd File."""
        # identical to bring in
        self._bring_in_default()