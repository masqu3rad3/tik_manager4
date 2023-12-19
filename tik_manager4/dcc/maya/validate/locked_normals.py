"""Locked Normals validation for Maya."""

from maya.api import OpenMaya
from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore

class LockedNormals(ValidateCore):
    """Validation for Locked Normals"""

    # Name of the validation
    name = "locked_normals"
    nice_name = "Locked Normals"

    def __init__(self):
        super(LockedNormals, self).__init__()
        self.autofixable = True
        self.ignorable = False
        self.selectable = True

        self.meshes_with_locked_normals = []

    def collect(self):
        """Collect all meshes."""
        self.collection = cmds.ls(type="mesh")

    def validate(self):
        """Check if the normals are locked for the meshes."""
        self.meshes_with_locked_normals = []
        self.collect()
        for mesh in self.collection:
            if self.unlock_normals(mesh, check_only=True):
                self.meshes_with_locked_normals.append(mesh)

        if self.meshes_with_locked_normals:
            self.failed(msg=f"Meshes with locked normals found: {self.meshes_with_locked_normals}")
        else:
            self.passed()

    def fix(self):
        """Fix the locked normals."""
        for mesh in self.meshes_with_locked_normals:
            self.unlock_normals(mesh, soften=True)

    def select(self):
        """Dummy select. Which selects all objects in the scene."""
        # do something to select the non-valid objects
        cmds.select(self.meshes_with_locked_normals)

    @staticmethod
    def unlock_normals(transform, soften=False, check_only=False):
        """Unlock the normals of the specified geometry.

        Args:
            transform (str or list): string or list of strings for the geometries
                to unlock.
            soften (bool, optional): If true, softens the edges with given
                softedge_angle value. Defaults to True.
            check_only: (Bool) If True, only checks the lock state and returns it. Does not unlock anything.
        """

        # Retrieve the MFnMesh api object.
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(transform)
        mfn_mesh = OpenMaya.MFnMesh(selection_list.getDagPath(0))
        # if its already unlocked, do not process again.
        lock_state = any(
            mfn_mesh.isNormalLocked(normal_index)
            for normal_index in range(mfn_mesh.numNormals)
        )
        if check_only:
            return lock_state
        if lock_state:
            mfn_mesh.unlockVertexNormals(OpenMaya.MIntArray(range(mfn_mesh.numVertices)))
        if soften:
            edge_ids = OpenMaya.MIntArray(range(mfn_mesh.numEdges))
            smooths = OpenMaya.MIntArray([True] * mfn_mesh.numEdges)
            mfn_mesh.setEdgeSmoothings(edge_ids, smooths)
            mfn_mesh.cleanupEdgeSmoothing()
            mfn_mesh.updateSurface()
        return True
