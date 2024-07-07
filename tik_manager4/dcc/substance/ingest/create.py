"""Create a new Substance Painter project with the given object."""

from pathlib import Path

from tik_manager4.ui.dialog.feedback import Feedback

import substance_painter

import os
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.substance import utils


class Create(IngestCore):
    """Create a new Substance Painter project with the given object."""

    nice_name = "Create Substance Project"
    valid_extensions = [".obj", ".fbx", ".dae", ".ply", ".gltf", ".glb", ".abc", ".usd", ".usda", ".usdc", ".usdz"]
    referencable = False

    def _bring_in_default(self):
        """Create Substance Painter Project."""
        if substance_painter.project.is_open():
            if substance_painter.project.needs_saving():
                feed = Feedback(parent=substance_painter.ui.get_main_window())
                res = feed.pop_question(title="Unsaved Changes",
                                  text="There are unsaved changes in the current project. Do you want to save them?",
                                  buttons=["yes", "no", "cancel"])
                if res == "yes":
                    if utils.get_scene_path():
                        substance_painter.project.save()
                    else:
                        save_action = utils.get_save_project_action()
                        save_action.trigger()
                elif feed.result == "cancel":
                    return
            substance_painter.project.close()

        uv_tile_workflow = substance_painter.project.ProjectWorkflow.UVTile
        ogl_normal_map_format = substance_painter.project.NormalMapFormat.OpenGL
        per_vertex_tangent = substance_painter.project.TangentSpace.PerVertex
        project_settings = substance_painter.project.Settings(
            import_cameras=True,
            normal_map_format=ogl_normal_map_format,
            tangent_space_mode=per_vertex_tangent,
            project_workflow=uv_tile_workflow,
        )

        substance_painter.project.create(mesh_file_path=self.ingest_path, settings=project_settings)