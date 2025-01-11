"""Extract FBX scene."""

import bpy

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.blender import utils


class FBX(ExtractCore):
    """Extract FBX scene"""

    nice_name = "FBX Scene"
    optional = False
    color = (255, 255, 0)

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
                "bake_animation": {
                    "display_name": "Bake Animation",
                    "type": "boolean",
                    "value": True,
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
                "bake_animation": {
                    "display_name": "Bake Animation",
                    "type": "boolean",
                    "value": True,
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
        super(FBX, self).__init__(exposed_settings=exposed_settings)

        self.extension = ".fbx"

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
            bpy.ops.export_scene.fbx(filepath=file_path,
                                     use_selection=False,
                                     apply_unit_scale=True,
                                     bake_space_transform=True)

    def _extract_animation(self):
        """Extract method for animation category"""
        settings = self.settings.get("Animation")
        file_path = self.resolve_output()
        start_frame = settings.get("start_frame")
        end_frame = settings.get("end_frame")
        bake_animation = settings.get("bake_animation")
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.export_scene.fbx(filepath=file_path,
                                     use_selection=False,
                                     apply_unit_scale=True,
                                     bake_space_transform=True,
                                     bake_anim=bake_animation,
                                     bake_anim_use_all_bones=True,
                                     bake_anim_force_startend_keying=True,
                                     bake_anim_start=start_frame,
                                     bake_anim_end=end_frame)

    def _extract_fx(self):
        """Extract method for fx category"""
        self._extract_animation()

    def _extract_layout(self):
        """Extract method for layout category"""
        settings = self.settings.get("Animation")
        file_path = self.resolve_output()
        start_frame = settings.get("start_frame")
        end_frame = settings.get("end_frame")
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.export_scene.fbx(filepath=file_path,
                                     use_selection=False,
                                     apply_unit_scale=True,
                                     bake_space_transform=True,
                                     bake_anim_start=start_frame,
                                     bake_anim_end=end_frame)

    def _extract_lighting(self):
        """Extract method for lighting category"""
        self._extract_layout()

    def _extract_default(self):
        """Extract for any non-specified category."""
        with bpy.context.temp_override(**utils.get_override_context()):
            bpy.ops.export_scene.fbx(filepath=self.resolve_output(),
                                     use_selection=False,
                                     apply_unit_scale=True,
                                     bake_space_transform=True)
