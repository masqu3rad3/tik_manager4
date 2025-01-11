"""Validation class missing UVs."""

from maya import OpenMaya as om
from maya import cmds

from tik_manager4.dcc.validate_core import ValidateCore

class MissingUvs(ValidateCore):
    """Validation class missing UVs."""

    nice_name = "Missing UVs"

    def __init__(self):
        super().__init__()
        self.autofixable = False
        self.ignorable = True
        self.selectable = True

        self.failed_meshes = []

    def collect(self):
        """Collect all meshes in the scene."""
        pass

    def validate(self):
        """Validate."""
        self.failed_meshes = self._check_for_missing_uvs()

        if self.failed_meshes:
            self.failed(msg=f"Overlapping UVs found on meshes: {self.failed_meshes}")
        else:
            self.passed()

    def select(self):
        """Dummy select. Which selects all objects in the scene."""
        # do something to select the non-valid objects
        cmds.select(self.failed_meshes)

    @staticmethod
    def _check_for_missing_uvs():
        iterations = om.MItDag(om.MItDag.kDepthFirst, om.MFn.kMesh)
        invalid_meshes = []

        while not iterations.isDone():
            dag_path = om.MDagPath()
            iterations.getPath(dag_path)

            mesh_fn = om.MFnMesh(dag_path)
            if mesh_fn.numUVs() == 0:
                invalid_meshes.append(dag_path.fullPathName())
            iterations.next()
        return invalid_meshes
