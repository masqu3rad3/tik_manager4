"""Example of a validation class for Maya."""

from maya import cmds
from maya import mel

from tik_manager4.dcc.validate_core import ValidateCore

class OverlappingUvs(ValidateCore):
    """Example validation for Maya"""

    # Name of the validation
    name = "overlapping_uvs"
    nice_name = "Overlapping UVs"

    def __init__(self):
        super(OverlappingUvs, self).__init__()
        self.autofixable = False
        self.ignorable = False
        self.selectable = True

        self.failed_meshes = []

    def collect(self):
        """Collect all meshes in the scene."""
        self.collection = cmds.ls(type="mesh")

    def validate(self):
        """Validate."""
        self.failed_meshes = []
        self.collect()
        for mesh in self.collection:
            if self.get_overlap_count(mesh):
                self.failed_meshes.append(mesh)
        if self.failed_meshes:
            self.failed(msg=f"Overlapping UVs found on meshes: {self.failed_meshes}")
        else:
            self.passed()

    def select(self):
        """Dummy select. Which selects all objects in the scene."""
        # do something to select the non-valid objects
        cmds.select(d=True)
        cmds.select(self.failed_meshes)
        cmds.selectMode(component=True)
        cmds.selectType(pf=True)
        cmds.select(d=True)
        mel.eval("selectUVOverlappingComponents 1 0")

    @staticmethod
    def get_overlap_count(mesh):
        """Checks the mesh for overlapping faces and returns the count. Returns None if 0"""
        cmds.select(mesh)
        cmds.selectMode(component=True)
        cmds.selectType(pf=True)
        cmds.select(deselect=True)
        mel.eval("selectUVOverlappingComponents 1 0")
        return len(cmds.ls(sl=True))
