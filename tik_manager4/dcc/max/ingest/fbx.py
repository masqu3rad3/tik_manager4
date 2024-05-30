"""Ingest FBX."""

from pathlib import Path
import pymxs
from pymxs import runtime as rt

from tik_manager4.dcc.ingest_core import IngestCore


class Fbx(IngestCore):
    """Ingest FBX."""

    nice_name = "Ingest fbx"
    valid_extensions = [".fbx"]
    referencable = False

    def __init__(self):
        super().__init__()
        if not rt.pluginManager.loadclass(rt.FBXIMP):
            raise ValueError("FBX Plugin cannot be initialized")
        self.category_functions = {
            "Model": self._bring_in_model,
            "Rig": self._bring_in_default,
            "Layout": self._bring_in_layout,
            "Animation": self._bring_in_animation,
            "Fx": self._bring_in_fx,
            "Lighting": self._bring_in_lighting,
        }

    def __set_values(self, settings_dict):
        """Set the FBX values from the value_dict.

        Args:
            settings_dict: (dict) Dictionary containing the values to set.
        """

        rt.FBXImporterSetParam('ResetImport')
        for key, value in settings_dict.items():
            rt.FBXImporterSetParam(rt.Name(key), value)

    def _bring_in_model(self):
        """Import FBX file."""
        settings_dict = {
            "Mode": "create",
            "Animation": False
        }
        self.__set_values(settings_dict)
        rt.importFile(self.ingest_path, rt.Name("NoPrompt"), using=rt.FBXIMP)

    def _bring_in_animation(self):
        """Import FBX file."""
        settings_dict = {
            "Mode": "merge",
            "Animation": True
        }
        self.__set_values(settings_dict)
        rt.importFile(self.ingest_path, rt.Name("NoPrompt"), using=rt.FBXIMP)

    def _bring_in_layout(self):
        """Import FBX file."""
        self._bring_in_animation()

    def _bring_in_fx(self):
        """Import FBX file."""
        self._bring_in_animation()

    def _bring_in_lighting(self):
        """Import FBX file."""
        self._bring_in_animation()

    def _bring_in_default(self):
        """Import FBX file."""
        self.__set_values({})
        rt.importFile(self.ingest_path, rt.Name("NoPrompt"), using=rt.FBXIMP)