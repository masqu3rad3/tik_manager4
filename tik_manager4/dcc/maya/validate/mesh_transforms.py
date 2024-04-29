"""Example of a validation class for Maya."""

from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore

class MeshTransform(ValidateCore):
    """Example validation for Maya"""

    nice_name = "Mesh Transforms"

    def __init__(self):
        super(MeshTransform, self).__init__()
        self.autofixable = True
        self.ignorable = False
        self.selectable = True

        self.non_frozen_meshes = []

    def collect(self):
        """Collect all mesh transforms in the scene."""
        all_meshes = cmds.ls(type="mesh")
        self.collection = [cmds.listRelatives(mesh, parent=True)[0] for mesh in all_meshes]

    def _check_frozen(self, mesh_transform):
        """Check if the mesh transform is frozen."""
        for attr in "tr":
            if cmds.getAttr("{}.{}".format(mesh_transform, attr)) != [(0.0, 0.0, 0.0)]:
                return False
        if cmds.getAttr("{}.s".format(mesh_transform)) != [(1.0, 1.0, 1.0)]:
            return False
        return True

    def validate(self):
        """Check if the mesh transforms are not frozen."""
        self.collect()
        self.non_frozen_meshes = []
        for mesh_transform in self.collection:
            if not self._check_frozen(mesh_transform):
                self.non_frozen_meshes.append(mesh_transform)

        if self.non_frozen_meshes:
            self.failed(msg=f"Non-frozen mesh transforms found: {self.non_frozen_meshes}")
        else:
            self.passed()

    def fix(self):
        """Freeze all non-frozen meshes."""
        for mesh_transform in self.non_frozen_meshes:
            cmds.makeIdentity(mesh_transform, apply=True)
        self.passed()

    def select(self):
        """Select the non-frozen meshes."""
        cmds.select(self.non_frozen_meshes)
