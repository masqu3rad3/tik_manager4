"""Extract USD scene."""

import bpy

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.blender import utils


class Usd(ExtractCore):
    """Extract USD scene"""

    nice_name = "USD Scene"
    optional = False
    color = (71, 143, 203)

    def __init__(self):
        _ranges = utils.get_ranges()
        # these are the exposed settings in the UI
        exposed_settings = {
            "Animation": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _ranges[0],
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _ranges[3],
                }
            },
            "Fx": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _ranges[0],
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _ranges[3],
                }
            },
            "Layout": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _ranges[0],
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _ranges[3],
                }
            },
            "Lighting": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _ranges[0],
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _ranges[3],
                }
            },
        }
        super(Usd, self).__init__(exposed_settings=exposed_settings)

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
            bpy.ops.wm.usd_export(**utils.get_usd_export_kwargs(file_path))

    def _extract_animation(self):
        """Extract method for animation category"""
        backup_ranges = utils.get_ranges()
        start_frame = self.settings.get_sub
        utils.set_ranges(self.settings["Animation"].get("start_frame"),
                         self.settings["Animation"].get("end_frame")
                         )

        file_path = self.resolve_output()
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.usd_export(**utils.get_usd_export_kwargs(file_path))

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
