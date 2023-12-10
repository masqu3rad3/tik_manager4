"""Extract FBX from Maya scene."""

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.maya import fbx_utility as fbxu
from tik_manager4.dcc.extract_core import ExtractCore



class Fbx(ExtractCore):
    """Extract FBX from Maya scene."""
    name = "fbx" # IMPORTANT. Must match to the one in category_definitions.json
    nice_name = "FBX"
    color = (244, 132, 132)
    def __init__(self):
        super().__init__()
        if not cmds.pluginInfo("fbxmaya", loaded=True, query=True):
            try:
                cmds.loadPlugin("fbxmaya")
            except Exception as exc: # pylint: disable=broad-except
                om.MGlobal.displayInfo("FBX Plugin cannot be initialized")
                raise exc

        self._extension = ".fbx"
        self.category_functions = {"Model": self._extract_model,
                                   "Layout": self._extract_layout,
                                   "Animation": self._extract_animation,
                                   "Rig": self._extract_rig
                                   }

    def _extract_model(self, selected=False):
        """Extract method for model category"""
        _file_path = self.resolve_output()
        fbxu.save(_file_path, selection_only=selected, animation=False, skins=False, blend_shapes=False, cameras=False, lights=False, audio=False)

    def _extract_layout(self, selected=False):
        """Extract method for layout category"""
        _file_path = self.resolve_output()
        fbxu.save(_file_path, selection_only=selected, animation=True, skins=True, blend_shapes=True, cameras=True, lights=True, audio=True)

    def _extract_animation(self, selected=False):
        """Extract method for animation category"""
        _file_path = self.resolve_output()
        fbxu.save(_file_path, selection_only=selected, animation=True, animation_only=True)

    def _extract_rig(self, selected=False):
        """Extract method for rig category"""
        _file_path = self.resolve_output()
        fbxu.save(_file_path, selection_only=selected, animation=False, skins=True, blend_shapes=True)

    def _extract_default(self, selected=False):
        """Extract method for any non-specified category"""
        fbxu.save(self.resolve_output(), selection_only=selected)