"""Main module for Maya DCC integration."""

import logging
from pathlib import Path

import bpy

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.blender import validate
from tik_manager4.dcc.blender import extract
from tik_manager4.dcc.blender import ingest
from tik_manager4.dcc.blender import utils

LOG = logging.getLogger(__name__)



class Dcc(MainCore):
    """Maya DCC class."""

    name = "Blender"
    formats = [".blend"]  # File formats supported by the DCC
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
        initial_use_file_extension = bpy.context.scene.render.use_file_extension

        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.resolution_x = width * 10
        bpy.context.scene.render.resolution_y = height * 10
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.frame_set(self.get_current_frame())

        # Render the single frame
        # bpy.ops.render.render(write_still=True)
        context = utils.get_override_context()
        with bpy.context.temp_override(**context):
            bpy.ops.render.opengl(write_still=True)

        # we saved the image 10 times bigger than the desired size, so we need to resize it
        # load
        bpy.ops.image.open(filepath=file_path)
        # get the loaded image
        file_name = Path(file_path).name
        image = bpy.data.images[file_name]

        image.scale(width, height)
        image.save()
        # remove it from the scene data
        bpy.data.images.remove(image)

        # Restore the initial settings
        bpy.context.scene.render.image_settings.file_format = initial_file_format
        bpy.context.scene.render.filepath = initial_filepath
        bpy.context.scene.render.resolution_x = initial_resolution_x
        bpy.context.scene.render.resolution_y = initial_resolution_y
        bpy.context.scene.render.resolution_percentage = initial_resolution_percentage

        return file_path

    @staticmethod
    def get_scene_cameras():
        """
        Return a dictionary of all the cameras in the scene where key is the camera name and value is the camera path.
        """
        all_camera_nodes = [node for node in bpy.context.scene.objects if node.type == 'CAMERA']
        camera_dict = {}
        for camera in all_camera_nodes:
            camera_dict[camera.name] = camera
        return camera_dict

    @staticmethod
    def get_current_camera():
        """Return the current camera name and node."""
        camera_node = bpy.context.scene.camera
        if camera_node:
            return camera_node.name, camera_node
        return "View", ""


    def generate_preview(self, name, folder, camera_code, resolution, range, settings=None):
        """
        Create a preview from the current scene
        Args:
            name: (String) Name of the preview
            folder: (String) Folder to save the preview
            camera_code: (String) Camera code. In Maya, this is the UUID of the camera transform node.
            resolution: (list) Resolution of the preview
            range: (list) Range of the preview
            settings: (dict) Global Settings dictionary
        """

        # store the initial settings from the scene to restore them later
        initial_file_format = bpy.context.scene.render.image_settings.file_format
        initial_filepath = bpy.context.scene.render.filepath
        initial_resolution_x = bpy.context.scene.render.resolution_x
        initial_resolution_y = bpy.context.scene.render.resolution_y
        initial_resolution_percentage = bpy.context.scene.render.resolution_percentage
        initial_frame_start = bpy.context.scene.frame_start
        initial_frame_end = bpy.context.scene.frame_end

        extension = "mp4" # blender is smart...

        file_path = str(Path(folder) / f"{name}.{extension}")

        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.frame_set(self.get_current_frame())

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