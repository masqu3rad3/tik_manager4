"""Extract FBX from 3ds Max Scene"""

import pymxs
from pymxs import runtime as rt

from tik_manager4.dcc.extract_core import ExtractCore


class Fbx(ExtractCore):
    """Extract FBX from 3ds Max scene."""

    nice_name = "FBX"
    color = (255, 255, 0)
    bundled = False
    _range_start = float(rt.animationRange.start)
    _range_end = float(rt.animationRange.end)

    # these are the exposed settings in the UI
    exposed_settings = {
        "Animation": {
            "start_frame":_range_start,
            "end_frame": _range_end,
            "sub_steps": 1,
            "bake_animation": False,
            "bake_resample_all": False,
        },
        "Layout": {
            "start_frame": _range_start,
            "end_frame": _range_end,
        },
        "Fx": {
            "start_frame": _range_start,
            "end_frame": _range_end,
            "sub_steps": 1,
            "Selection_set_export": False,
            "selection_set": " ",
        },
        "Lighting": {
            "start_frame": _range_start,
            "end_frame": _range_end,
        }
    }

    def __init__(self):
        super().__init__()
        if not rt.pluginManager.loadclass(rt.FBXEXP):
            raise ValueError("FBX Plugin cannot be initialized")
        self._extension = ".fbx"
        self.category_functions = {
            "Model": self._extract_model,
            "Rig": self._extract_rig,
            "Animation": self._extract_animation,
            "Layout": self._extract_layout,
            "Fx": self._extract_fx,
            "Lighting": self._extract_lighting,
        }

    def __set_values(self, settings_dict):
        """Set the FBX values from the value_dict.

        Args:
            settings_dict: (dict) Dictionary containing the values to set.
        """

        rt.FBXExporterSetParam('ResetExport')
        for key, value in settings_dict.items():
            rt.FBXExporterSetParam(rt.Name(key), value)

    def _extract_model(self, selected=False):
        """Extract FBX from 3ds Max scene.

        Args:
            selected: (bool) If True, only selected objects will be exported.
        """
        # FBX export does not support ranges. For our purposes we will
        # use the same _extract_model function for all categories.
        # FBX export exports the whole scene. We don't need to select anything.
        file_path = self.resolve_output()
        settings_dict = {
            "Animation": False,
            "Skin": False,
            "Shape": False,
            "Cameras": False,
            "Lights": False,
        }
        self.__set_values(settings_dict)

        rt.exportFile(
            file_path,
            rt.name("NoPrompt"),
            selectedOnly=selected,
            using=rt.FBXEXP
        )

    def _extract_animation(self):
        """Extract FBX from 3ds Max scene."""
        file_path = self.resolve_output()
        settings = self.settings.get("Animation", {})
        settings_dict = {
            "Animation": True,
            "BakeAnimation": settings.get_property("bake_animation"),
            "BakeFrameStart": settings.get_property("start_frame"),
            "BakeFrameEnd": settings.get_property("end_frame"),
            "BakeFrameStep": settings.get_property("sub_steps"),
            "BakeResampleAnimation": settings.get_property("bake_resample_all"),
            "Skin": True,
            "Shape": True,
            "Cameras": True,
            "Lights": False,
        }
        self.__set_values(settings_dict)

        rt.exportFile(
            file_path,
            rt.name("NoPrompt"),
            selectedOnly=False,
            using=rt.FBXEXP
        )

    def _extract_layout(self):
        """Extract FBX from 3ds Max scene."""
        file_path = self.resolve_output()
        settings = self.settings.get("Layout", {})
        settings_dict = {
            "Animation": True,
            "BakeAnimation": settings.get_property("bake_animation"),
            "BakeFrameStart": settings.get_property("start_frame"),
            "BakeFrameEnd": settings.get_property("end_frame"),
            "BakeFrameStep": settings.get_property("sub_steps"),
            "BakeResampleAnimation": settings.get_property("bake_resample_all"),
            "Skin": True,
            "Shape": True,
            "Cameras": True,
            "Lights": True,
        }
        self.__set_values(settings_dict)

        rt.exportFile(
            file_path,
            rt.name("NoPrompt"),
            selectedOnly=False,
            using=rt.FBXEXP
        )

    def _extract_fx(self):
        """Extract FBX from 3ds Max scene."""
        file_path = self.resolve_output()
        settings = self.settings.get("Fx", {})
        settings_dict = {
            "Animation": True,
            "BakeAnimation": True,
            "BakeFrameStart": settings.get_property("start_frame"),
            "BakeFrameEnd": settings.get_property("end_frame"),
            "BakeFrameStep": settings.get_property("sub_steps"),
            "BakeResampleAnimation": True,
            "SelectionSetExport": settings.get_property("Selection_set_export"),
            "SelectionSet": settings.get_property("selection_set"),
            "Skin": True,
            "Shape": True,
            "Cameras": False,
            "Lights": False,
        }
        self.__set_values(settings_dict)

        rt.exportFile(
            file_path,
            rt.name("NoPrompt"),
            selectedOnly=False,
            using=rt.FBXEXP
        )

    def _extract_rig(self):
        """Extract FBX from 3ds Max scene."""
        file_path = self.resolve_output()
        settings_dict = {
            "Animation": False,
            "Skin": True,
            "Shape": True,
            "Cameras": False,
            "Lights": False,
        }
        self.__set_values(settings_dict)

        rt.exportFile(
            file_path,
            rt.name("NoPrompt"),
            selectedOnly=False,
            using=rt.FBXEXP
        )

    def _extract_lighting(self):
        """Extract method for lighting category"""
        # identical to layout
        self._extract_layout()

    def _extract_default(self):
        """Extract method for any non-specified category"""
        file_path = self.resolve_output()
        self.__set_values({})
        rt.exportFile(
            file_path,
            rt.name("NoPrompt"),
            selectedOnly=False,
            using=rt.FBXEXP
        )