"""Extract Alembic scene."""

import bpy

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.blender import utils


class Alembic(ExtractCore):
    """Extract Alembic scene"""

    nice_name = "Alembic Scene"
    optional = False
    color = (244, 132, 132)


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
                },
                "sub_steps": {
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
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
                },
                "sub_steps": {
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
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
                },
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
                },
            },
        }
        super(Alembic, self).__init__(exposed_settings=exposed_settings)

        self.extension = ".abc"

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
            bpy.ops.wm.alembic_export(filepath=file_path,
                                      uvs=True,
                                      normals=True,
                                      )

    def _extract_animation(self):
        """Extract method for animation category"""
        settings = self.settings.get("Animation")
        file_path = self.resolve_output()
        start_frame = settings.get("start_frame")
        end_frame = settings.get("end_frame")
        sub_steps = settings.get("sub_steps")
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.alembic_export(filepath=file_path,
                                      start=start_frame,
                                      end=end_frame,
                                      xsamples=sub_steps,
                                      gsamples=sub_steps,
                                      )

    def _extract_fx(self):
        """Extract method for fx category"""
        # identical to animation
        self._extract_animation()

    def _extract_layout(self):
        """Extract method for fx category"""
        settings = self.settings.get("Animation")
        file_path = self.resolve_output()
        start_frame = settings.get("start_frame")
        end_frame = settings.get("end_frame")
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.alembic_export(filepath=file_path,
                                      start=start_frame,
                                      end=end_frame,
                                      )

    def _extract_lighting(self):
        """Extract method for lighting category"""
        # identical to layout
        self._extract_layout()

    def _extract_default(self):
        """Extract for any non-specified category."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.wm.usd_export(filepath=self.resolve_output())
