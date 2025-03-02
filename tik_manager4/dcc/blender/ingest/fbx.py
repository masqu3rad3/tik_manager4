"""Ingest FBX."""

import bpy

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.blender import utils


class FBX(IngestCore):
    """Ingest FBX."""

    nice_name = "Ingest FBX"
    valid_extensions = [".fbx"]
    referencable = False

    def __init__(self):
        super(FBX, self).__init__()

        self.category_functions = {
            "Model": self._bring_in_model,
            "Animation": self._bring_in_animation,
            "Fx": self._bring_in_fx,
            "Layout": self._bring_in_layout,
            "Lighting": self._bring_in_lighting,
        }

    def _bring_in_default(self):
        """Import FBX File."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.import_scene.fbx(filepath=self.ingest_path)

    def _bring_in_model(self):
        """Import FBX File."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.import_scene.fbx(filepath=self.ingest_path,
                                     use_custom_normals=True)

    def _bring_in_animation(self):
        """Import FBX File."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.import_scene.fbx(filepath=self.ingest_path,
                                     use_custom_normals=True,
                                     bake_anim=True)

    def _bring_in_fx(self):
        """Import FBX File."""
        self._bring_in_animation()

    def _bring_in_layout(self):
        """Import FBX File."""
        self._bring_in_animation()

    def _bring_in_lighting(self):
        """Import FBX File."""
        self._bring_in_animation()

    def _reference_default(self):
        """Reference FBX File."""
        # identical to bring in
        self._bring_in_default()
