"""Example of a validation class for Maya."""

from maya import cmds
from maya import mel

from tik_manager4.dcc.validate_core import ValidateCore
from tik_manager4.dcc.maya import utils

class OverlappingUvs(ValidateCore):
    """Example validation for Maya"""

    # Name of the validation
    name = "overlapping_uvs"
    nice_name = "Overlapping UVs"

    def __init__(self):
        super(OverlappingUvs, self).__init__()
        self.autofixable = False
        self.ignorable = True
        self.selectable = True

        self.failed_meshes = []
        self.overlaps = []

    def collect(self):
        """Collect all meshes in the scene."""
        self.collection = cmds.ls(type="mesh")

    def validate(self):
        """Validate."""
        self.failed_meshes = []
        self.overlaps = []
        self.collect()
        for mesh in self.collection:
            # if self.get_overlap_count(mesh):
            overlaps = self.get_overlapping_uvs(mesh)
            if overlaps:
                self.failed_meshes.append(mesh)
                self.overlaps.extend(overlaps)
        if self.failed_meshes:
            self.failed(msg=f"Overlapping UVs found on meshes: {self.failed_meshes}")
        else:
            self.passed()

    def select(self):
        """Dummy select. Which selects all objects in the scene."""
        # do something to select the non-valid objects
        cmds.select(self.overlaps)

    def get_overlapping_uvs(self, shape):
        """Checks the mesh for overlapping faces and returns the count. Returns None if 0"""
        overlaps = cmds.polyUVOverlap(f"{shape}.f[*]", overlappingComponents=True)
        return overlaps

