"""Extract USD scene."""

import bpy

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.blender import utils


class Usd(ExtractCore):
    """Extract USD scene"""

    nice_name = "USD Scene"
    optional = False
    color = (71, 143, 203)
    _ranges = utils.get_ranges()

    # these are the exposed settings in the UI
    exposed_settings = {
        "Animation": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
        "Fx": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
        "Layout": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
        "Lighting": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
    }

    def __init__(self):
        super(Usd, self).__init__()

        self.extension = ".usd"

        # Category names must match to the ones in category_definitions.json (case sensitive)
        self.category_functions = {
            "Model": self._extract_model,
            "Animation": self._extract_animation,
            "Fx": self._extract_fx,
            "Layout": self._extract_layout,
            "Lighting": self._extract_lighting,
        }

    def _extract_model(self):
        """Extract method for model category"""
        file_path = self.resolve_output()
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.usd_export(filepath=file_path,
                                  export_animation=False,
                                  export_uvmaps=True,
                                  export_hair=True,
                                  export_materials=True,
                                  export_mesh_colors=True,
                                  export_textures=True
                                  )

    def _extract_animation(self):
        """Extract method for animation category"""
        backup_ranges = utils.get_ranges()
        utils.set_ranges(self.settings["Animation"]["start_frame"],
                         self.settings["Animation"]["end_frame"]
                         )

        file_path = self.resolve_output()
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.usd_export(filepath=file_path,
                                  export_animation=True,
                                  export_uvmaps=True,
                                  export_hair=True,
                                  export_materials=True,
                                  export_mesh_colors=True,
                                  export_textures=True
                                  )

        utils.set_ranges(backup_ranges)

    def _extract_layout(self):
        """Extract method for fx category"""
        self._extract_animation()

    def _extract_fx(self):
        """Extract method for fx category"""
        # identical to animation
        self._extract_animation()

    def _extract_lighting(self):
        """Extract method for lighting category"""
        # identical to animation
        self._extract_animation()

    def _extract_default(self):
        """Extract for any non-specified category."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.usd_export(filepath=self.resolve_output())
