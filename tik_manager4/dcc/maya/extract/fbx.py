"""Extract FBX from Maya scene."""

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.maya import fbx_utility as fbxu
from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.maya import utils


class Fbx(ExtractCore):
    """Extract FBX from Maya scene."""

    nice_name = "FBX"
    color = (255, 255, 0)
    # _ranges = utils.get_ranges()

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
                "bake_animation": {
                    "display_name": "Bake Animation",
                    "type": "boolean",
                    "value": False,
                },
                "bake_resample_all": {
                    "display_name": "Bake Resample All",
                    "type": "boolean",
                    "value": False,
                },
                "animation_only": {
                    "display_name": "Animation Only",
                    "type": "boolean",
                    "value": False,
                    "tooltip": "Export only the animation data",
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
                },
                "animation_only": {
                    "display_name": "Animation Only",
                    "type": "boolean",
                    "value": False,
                    "tooltip": "Export only the animation data",
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
                },
                "sub_steps": {
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
                "geometry_cache": {
                    "display_name": "Geometry Cache",
                    "type": "boolean",
                    "value": False,
                    "disables": [[False, "geometry_cache_set"]],
                },
                "geometry_cache_set": {
                    "display_name": "Geometry Cache Set",
                    "type": "string",
                    "value": " ",
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
            }
        }
        super().__init__(exposed_settings=exposed_settings, global_exposed_settings=None)
        if not cmds.pluginInfo("fbxmaya", loaded=True, query=True):
            try:
                cmds.loadPlugin("fbxmaya")
            except Exception as exc:  # pylint: disable=broad-except
                om.MGlobal.displayInfo("FBX Plugin cannot be initialized")
                raise exc

        self._extension = ".fbx"
        self.category_functions = {
            "Model": self._extract_model,
            "Rig": self._extract_rig,
            "Animation": self._extract_animation,
            "Layout": self._extract_layout,
            "Fx": self._extract_fx,
            "Lighting": self._extract_lighting,
        }

    def _extract_model(self, selected=False):
        """Extract method for model category"""
        _file_path = self.resolve_output()
        fbxu.save(
            _file_path,
            selection_only=selected,
            animation=False,
            skins=False,
            blend_shapes=False,
            cameras=False,
            lights=False,
            audio=False,
        )

    def _extract_animation(self):
        """Extract method for animation category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Animation")
        fbxu.save(
            _file_path,
            selection_only=False,
            animation=True,
            animation_only=settings.get("animation_only"),
            bake_animation=settings.get("bake_animation"),
            bake_start=settings.get("start_frame"),
            bake_end=settings.get("end_frame"),
            bake_step=settings.get("sub_steps"),
            bake_resample_all=settings.get("bake_resample_all"),
            audio=True,
        )

    def _extract_layout(self):
        """Extract method for layout category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Layout")
        fbxu.save(
            _file_path,
            selection_only=False,
            animation=True,
            animation_only=settings.get("animation_only"),
            bake_animation=settings.get("bake_animation"),
            bake_start=settings.get("start_frame"),
            bake_end=settings.get("end_frame"),
            bake_step=settings.get("sub_steps"),
            bake_resample_all=settings.get("bake_resample_all"),
            cameras=True,
            lights=True,
            audio=True,
        )

    def _extract_fx(self):
        """Extract method for fx category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Fx")
        fbxu.save(
            _file_path,
            selection_only=False,
            animation=True,
            animation_only=False,
            bake_animation=True,
            bake_start=settings.get("start_frame"),
            bake_end=settings.get("end_frame"),
            bake_step=settings.get("sub_steps"),
            bake_resample_all=True,
            geometry_cache=settings.get("geometry_cache"),
            geometry_cache_set=settings.get("geometry_cache_set"),
            cameras=False,
            lights=False,
            audio=False,
        )

    def _extract_rig(self):
        """Extract method for rig category"""
        _file_path = self.resolve_output()
        fbxu.save(
            _file_path,
            selection_only=False,
            animation=False,
            skins=True,
            blend_shapes=True,
            cameras=False,
            lights=False,
            audio=False,
        )

    def _extract_lighting(self):
        """Extract method for lighting category"""
        # identical to layout
        self._extract_layout()

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        fbxu.save(_file_path)
