"""Ensure meshes do not contain ngons"""

import bpy
from tik_manager4.dcc.validate_core import ValidateCore


class Ngons(ValidateCore):
    """Example validation for Blender"""

    nice_name = "Ngons"

    def __init__(self):
        super(Ngons, self).__init__()
        self.autofixable = False
        self.ignorable = True
        self.selectable = True
        self.bad_meshes = []

    def collect(self):
        """Collect all mesh objects in the scene."""
        self.collection = [
            obj for obj in bpy.context.scene.objects if obj.type == "MESH"
        ]

    def validate(self):
        """Identify ngons in the scene."""
        self.bad_meshes = []
        self.collect()
        for mesh in self.collection:
            ngon_count = self.get_ngon_count(mesh)
            if ngon_count:
                self.bad_meshes.append(mesh.name)
        if self.bad_meshes:
            self.failed(
                msg="Ngons found in the following meshes: {}".format(self.bad_meshes)
            )
        else:
            self.passed()

    def select(self):
        """Select the bad meshes with ngons."""
        bpy.ops.object.select_all(action="DESELECT")
        for mesh_name in self.bad_meshes:
            obj = bpy.data.objects.get(mesh_name)
            if obj:
                obj.select_set(True)

    def get_ngon_count(self, obj):
        """Check the mesh for ngons and return the count. Returns 0 if none found."""
        if obj.type != "MESH":
            return 0

        mesh = obj.data
        return sum(1 for poly in mesh.polygons if len(poly.vertices) > 4)
