"""Extract STL from Maya Scene"""

from pathlib import Path

from maya import cmds
from maya import OpenMaya as om

from tik_manager4.dcc.extract_core import ExtractCore


class Stl(ExtractCore):
    """Extract STL from Maya scene."""

    nice_name = "STL"
    color = (100, 200, 0)

    def __init__(self):
        super().__init__()
        if not cmds.pluginInfo("stlTranslator", loaded=True, query=True):
            try:
                cmds.loadPlugin("stlTranslator")
            except Exception as e:
                om.MGlobal.displayInfo("STL Plugin cannot be initialized")
                raise e

        om.MGlobal.displayInfo("STL Extractor loaded")

        self._extension = ".stl"
        self._bundled = True
        # we don't need to define category functions for STL

    @staticmethod
    def collect():
        """Collect bundle data from the scene."""
        meshes = cmds.ls(type="mesh")
        mesh_transforms = cmds.listRelatives(meshes, parent=True, fullPath=True)
        return mesh_transforms

    def _extract_default(self):
        """Extract STL from Maya scene."""
        # STL files are not supporting ranges. For our purposes we will
        # use the same _extract_default function for all categories.
        # STL export exports the each mesh separately. We need to have a bundle
        # directory which will hold all meshes.
        bundle_meshes = self.collect()
        if not bundle_meshes:
            om.MGlobal.displayInfo("No meshes found in the scene.")
            raise ValueError("No meshes found in the scene.")

        bundle_directory = self.resolve_output()
        # create the path if it doesn't exist
        Path(bundle_directory).mkdir(parents=True, exist_ok=True)

        for mesh in bundle_meshes:
            cmds.select(mesh)
            nice_name = mesh.split("|")[-1] # get the last part of the DAG path
            file_path = Path(bundle_directory, f"{nice_name}.stl")
            cmds.file(
                file_path,
                force=True,
                options="v=0;",
                type="STLExport",
                exportSelected=True,
            )
