"""Main module for Maya DCC integration."""

import logging

import bpy

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.blender import validate
from tik_manager4.dcc.blender import extract
from tik_manager4.dcc.blender import ingest
from tik_manager4.dcc.blender import utils

LOG = logging.getLogger(__name__)
class Dcc(MainCore):
    """Maya DCC class."""

    name = "NAME OF THE DCC"
    formats = [".blender"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    # Override the applicable methods from the MainCore class

    @staticmethod
    def save_scene():
        """Save the current scene."""
        bpy.ops.wm.save_mainfile()

    def save_as(self, file_path):
        """Save the current file to the given path."""
        bpy.ops.wm.save_as_mainfile(filepath=file_path)
        return file_path

    def open(self, file_path, force=True, **extra_arguments):
        """Open the given file path."""
        bpy.ops.wm.open_mainfile(filepath=file_path, display_file_selector=False)

    @staticmethod
    def get_ranges():
        """Get the frame range."""
        return utils.get_ranges()

    @staticmethod
    def set_ranges(range_list):
        """Set the frame range."""
        utils.set_ranges(range_list)

    @staticmethod
    def is_modified():
        """Return True if the scene is modified."""
        return bpy.data.is_dirty

    @staticmethod
    def get_scene_file():
        """Return the scene file."""
        return bpy.data.filepath

    @staticmethod
    def get_current_frame():
        """Return the current frame."""
        return bpy.context.scene.frame_current

    def generate_thumbnail(self, file_path, width, height):
        """Generate a thumbnail for the scene."""
        # store the initial settings from the scene to restore them later
        initial_file_format = bpy.context.scene.render.image_settings.file_format
        initial_filepath = bpy.context.scene.render.filepath
        initial_resolution_x = bpy.context.scene.render.resolution_x
        initial_resolution_y = bpy.context.scene.render.resolution_y
        initial_resolution_percentage = bpy.context.scene.render.resolution_percentage

        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.frame_set(self.get_current_frame())

        # Render the single frame
        bpy.ops.render.render(write_still=True)

        # Restore the initial settings
        bpy.context.scene.render.image_settings.file_format = initial_file_format
        bpy.context.scene.render.filepath = initial_filepath
        bpy.context.scene.render.resolution_x = initial_resolution_x
        bpy.context.scene.render.resolution_y = initial_resolution_y
        bpy.context.scene.render.resolution_percentage = initial_resolution_percentage

        return file_path

    @staticmethod
    def get_scene_cameras():
        """Return a list of cameras in the scene."""
        # TODO: Implement this method
        pass

    @staticmethod
    def get_current_camera():
        """Return the current camera."""
        # TODO: Implement this method
        pass

    @staticmethod
    def generate_preview(name, folder, camera=None, resolution=None, settings_file=None):
        """Generate a preview for the scene."""
        # TODO: Implement this method
        pass

    @staticmethod
    def get_dcc_version():
        """Return the DCC version."""
        return bpy.app.version_string

    @staticmethod
    def get_scene_fps():
        """Return the scene FPS."""
        return bpy.context.scene.render.fps

    @staticmethod
    def set_scene_fps(fps_value):
        """Set the scene FPS."""
        bpy.context.scene.render.fps = fps_value