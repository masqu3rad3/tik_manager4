"""Validation for overlapping UVs."""

from maya import cmds

from tik_manager4.dcc.validate_core import ValidateCore

class OverlappingUvs(ValidateCore):
    """Validation for overlapping UVs."""

    nice_name = "Overlapping UVs"

    def __init__(self):
        super().__init__()
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

    @staticmethod
    def get_overlapping_uvs(shape, batch_size=1000):
        faces = cmds.polyEvaluate(shape, face=True)
        overlapping_faces = []

        for i in range(0, faces, batch_size):
            end = min(i + batch_size + 100, faces - 1)  # Buffer overlap
            face_range = f"{shape}.f[{i}:{end}]"
            overlaps = cmds.polyUVOverlap(face_range, overlappingComponents=True)
            if overlaps:
                overlapping_faces.extend(overlaps)

        return overlapping_faces if overlapping_faces else None

