"""Ensure meshes does not contain ngons"""

from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore
from tik_manager4.dcc.maya import utils

class Ngons(ValidateCore):
    """Example validation for Maya"""

    nice_name = "Ngons"

    def __init__(self):
        super(Ngons, self).__init__()
        self.autofixable = False
        self.ignorable = True
        self.selectable = True

        self.bad_meshes = []

    def collect(self):
        """Collect all meshes in the scene."""
        self.collection = cmds.ls(type="mesh")

    def validate(self):
        """Identify the ngons in the scene."""
        self.bad_meshes = []
        self.collect()
        for mesh in self.collection:
            ngon_count = self.get_ngon_count(mesh)
            if ngon_count:
                self.bad_meshes.append(mesh)
        if self.bad_meshes:
            self.failed(msg=f"Ngons found in the following meshes: {self.bad_meshes}")
        else:
            self.passed()

    def select(self):
        """Select the bad meshes with ngons."""
        cmds.select(self.bad_meshes)

    @utils.keepselection
    def get_ngon_count(self, mesh):
        """Checks the mesh for ngons and returns the count of ngons. Returns None if 0"""
        cmds.select(mesh)
        cmds.selectType(smp=0, sme=1, smf=0, smu=0, pv=0, pe=1, pf=0, puv=0)
        cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
        cmds.polySelectConstraint(disable=True)
        return cmds.polyEvaluate(mesh, faceComponent=True)