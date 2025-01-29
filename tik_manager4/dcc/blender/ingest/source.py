"""Ingest Source Blender Scene."""

import bpy
from tik_manager4.dcc.ingest_core import IngestCore

class Source(IngestCore):
    """Ingest Source Blender Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".blend"]
    referencable = True

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Blender scene."""
        with bpy.data.libraries.load(self.ingest_path) as (data_from, data_to):
            data_to.objects = data_from.objects

        for obj in data_to.objects:
            bpy.context.scene.collection.objects.link(obj)
    def _reference_default(self):
        """Reference the Blender scene."""

        # Link/Append the objects from the specified collection
        with bpy.data.libraries.load(self.ingest_path, link=True) as (data_from, data_to):
            data_to.collections = data_from.collections

        # Link/Append the collection to the current scene
        for collection in data_to.collections:
            bpy.context.scene.collection.children.link(collection)
