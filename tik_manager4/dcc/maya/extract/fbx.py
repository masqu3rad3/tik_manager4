"""Extract FBX from Maya scene."""

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.maya import fbx_utility as fbxu
from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.maya import utils


class Fbx(ExtractCore):
    """Extract FBX from Maya scene."""

    name = "fbx"  # IMPORTANT. Must match to the one in category_definitions.json
    nice_name = "FBX"
    color = (255, 255, 0)
    _ranges = utils.get_ranges()

    # these are the exposed settings in the UI
    default_settings = {
        "Animation": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
            "bake_animation": False,
            "bake_resample_all": False,
        },
        "Layout": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
        "Fx": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
            "geometry_cache": False,
            "geometry_cache_set": " ",
        },
        "Lighting": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
    }

    def __init__(self):
        super().__init__()
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
        settings = self.settings.get("Animation", {})
        fbxu.save(
            _file_path,
            selection_only=False,
            animation=True,
            animation_only=True,
            bake_animation=settings.get_property("bake_animation"),
            bake_start=settings.get_property("start_frame"),
            bake_end=settings.get_property("end_frame"),
            bake_step=settings.get_property("sub_steps"),
            bake_resample_all=settings.get_property("bake_resample_all"),
            audio=True,
        )

    def _extract_layout(self):
        """Extract method for layout category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Layout", {})
        fbxu.save(
            _file_path,
            selection_only=False,
            animation=True,
            animation_only=True,
            bake_animation=settings.get_property("bake_animation"),
            bake_start=settings.get_property("start_frame"),
            bake_end=settings.get_property("end_frame"),
            bake_step=settings.get_property("sub_steps"),
            bake_resample_all=settings.get_property("bake_resample_all"),
            cameras=True,
            lights=True,
            audio=True,
        )

    def _extract_fx(self):
        """Extract method for fx category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Fx", {})
        fbxu.save(
            _file_path,
            selection_only=False,
            animation=True,
            animation_only=False,
            bake_animation=True,
            bake_start=settings.get_property("start_frame"),
            bake_end=settings.get_property("end_frame"),
            bake_step=settings.get_property("sub_steps"),
            bake_resample_all=True,
            geometry_cache=settings.get_property("geometry_cache"),
            geometry_cache_set=settings.get_property("geometry_cache_set"),
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
