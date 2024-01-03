"""Extract STL from 3ds Max Scene"""
from pathlib import Path

import pymxs
from pymxs import runtime as rt

from tik_manager4.dcc.extract_core import ExtractCore


class Stl(ExtractCore):
    """Extract STL from 3ds Max scene."""

    nice_name = "STL"
    color = (100, 200, 0)

    def __init__(self):
        super().__init__()
        self._extension = ".stl"
        self._bundled = True
        # we don't need to define category functions for STL

    @staticmethod
    def collect():
        """Collect bundle data from the scene."""
        meshes = rt.geometry
        return meshes

    def _extract_default(self):
        """Extract STL from 3ds Max scene."""
        # STL files are not supporting ranges. For our purposes we will
        # use the same _extract_default function for all categories.
        # STL export exports the each mesh separately. We need to have a bundle
        # directory which will hold all meshes.
        bundle_meshes = self.collect()
        if not bundle_meshes:
            pymxs.print_("No polygon mesh object found in the scene.")
            raise ValueError("No polygon mesh object found in the scene.")

        _str_directory = self.resolve_output()
        bundle_directory = Path(_str_directory)
        # create the path if it doesn't exist
        bundle_directory.mkdir(parents=True, exist_ok=True)

        for mesh in bundle_meshes:
            rt.select(mesh)
            nice_name = mesh.name
            file_path = bundle_directory / f"{nice_name}.stl"
            rt.select(mesh)
            rt.exportFile(
                file_path.as_posix(),
                rt.name("NoPrompt"),
                exportSelected=True,
                using=rt.STL_Export,
            )  # using binary format
