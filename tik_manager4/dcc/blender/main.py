"""Main module for Maya DCC integration."""

import logging
from pathlib import Path

import bpy

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.blender import validate
from tik_manager4.dcc.blender import extract
from tik_manager4.dcc.blender import ingest
from tik_manager4.dcc.blender import utils
from tik_manager4.dcc.blender import extension

LOG = logging.getLogger(__name__)


# def render_complete():
#     """Handler function to flag that the render is complete."""
#     return True

class Dcc(MainCore):
    """Maya DCC class."""

    name = "Blender"
    formats = [".blend"]  # File formats supported by the DCC
    preview_enabled = True  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes

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

    @utils.keep_scene_settings
    def generate_thumbnail(self, file_path, width, height):
        """Generate a thumbnail for the scene."""

        # get the extension from the file path
        extension = Path(file_path).suffix
        extension_map = {".jpg": 'JPEG', ".png": 'PNG'}

        bpy.context.scene.render.image_settings.file_format = extension_map.get(extension, 'JPEG')
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.resolution_x = width * 10
        bpy.context.scene.render.resolution_y = height * 10
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.frame_set(self.get_current_frame())
        bpy.context.scene.render.use_file_extension = True

        # Render the single frame
        # bpy.ops.render.render(write_still=True)
        context = utils.get_override_context()
        try:
            with bpy.context.temp_override(**context):
                bpy.ops.render.opengl(write_still=True)
        except TypeError:
            # the override context is not working in the newer versions of blender
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

        return file_path

    @staticmethod
    def get_scene_cameras():
        """
        Return a dictionary of all the cameras in the scene where key is the camera name and value is the camera path.
        """
        all_camera_nodes = [node for node in bpy.context.scene.objects if node.type == 'CAMERA']
        camera_dict = {"active": ""}
        for camera in all_camera_nodes:
            camera_dict[camera.name] = camera
        return camera_dict

    @staticmethod
    def get_current_camera():
        """Return the current camera name and node."""
        camera_node = bpy.context.scene.camera
        if camera_node:
            return camera_node.name, camera_node
        return "active", ""

    @staticmethod
    def set_camera(camera_node):
        """Set the viewport camera to the given camera."""
        if not camera_node == "":
            bpy.context.scene.camera = camera_node
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == "VIEW_3D":
                        area.spaces[0].region_3d.view_perspective = "CAMERA"
                        return
        return

    @utils.keep_scene_settings
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

        extension = "mp4" # blender is smart...

        settings = settings or {
            "DisplayFieldChart": False,
            "DisplayGateMask": False,
            "DisplayFilmGate": False,
            "DisplayFilmOrigin": False,
            "DisplayFilmPivot": False,
            "DisplayResolution": False,
            "DisplaySafeAction": False,
            "DisplaySafeTitle": False,
            "DisplayAppearance": "smoothShaded",
            "ClearSelection": True,
            "ShowFrameNumber": True,
            "ShowFrameRange": True,
            "CrfValue": 23,
            "Format": "video",
            "PostConversion": True,
            "ShowFPS": True,
            "PolygonOnly": True,
            "Percent": 100,
            "DisplayTextures": True,
            "ShowGrid": False,
            "ShowSceneName": False,
            "UseDefaultMaterial": False,
            "ViewportAsItIs": False,
            "HudsAsItIs": False,
            "WireOnShaded": False,
            "Codec": "png",
            "ShowCategory": False,
            "Quality": 100,
        }

        file_path = str(Path(folder) / f"{name}.{extension}")

        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.render.pixel_aspect_x = 1.0
        bpy.context.scene.render.pixel_aspect_y = 1.0
        bpy.context.scene.render.use_border = False
        bpy.context.scene.render.fps = self.get_scene_fps()

        utils.set_ranges(range)
        bpy.context.scene.frame_step = 1
        bpy.context.scene.render.frame_map_old = 100
        bpy.context.scene.render.frame_map_new = 100
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.use_file_extension = True
        bpy.context.scene.render.use_render_cache = False
        bpy.context.scene.render.image_settings.file_format = "FFMPEG"
        bpy.context.scene.render.image_settings.color_mode = "RGB"
        # TODO: This can be set from the settings if there is a metadata for it
        bpy.context.scene.render.image_settings.color_management = "FOLLOW_SCENE"
        bpy.context.scene.render.ffmpeg.format = "MPEG4"
        bpy.context.scene.render.ffmpeg.constant_rate_factor = "HIGH"
        bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        bpy.context.scene.render.ffmpeg.audio_codec = 'AAC'

        # set the existing metadatas as per the settings
        bpy.context.scene.render.metadata_input = "SCENE"
        bpy.context.scene.render.use_stamp_date = False
        bpy.context.scene.render.use_stamp_time = False
        bpy.context.scene.render.use_stamp_render_time = False
        bpy.context.scene.render.use_stamp_frame = settings.get("ShowFrameNumber", False)
        bpy.context.scene.render.use_stamp_frame_range = settings.get("ShowFrameRange", False)
        bpy.context.scene.render.use_stamp_memory = False
        bpy.context.scene.render.use_stamp_hostname = False
        bpy.context.scene.render.use_stamp_camera = False
        bpy.context.scene.render.use_stamp_lens = False
        bpy.context.scene.render.use_stamp_scene = False
        bpy.context.scene.render.use_stamp_marker = False
        bpy.context.scene.render.use_stamp_filename = False
        bpy.context.scene.render.use_stamp_sequencer_strip = False
        # we will use the note section to show the FPS
        if settings.get('ShowFPS', False):
            bpy.context.scene.render.use_stamp_note = True
            bpy.context.scene.render.stamp_note_text = f"FPS: {self.get_scene_fps()}"

        else:
            bpy.context.scene.render.use_stamp_note = False

        bpy.context.scene.render.use_stamp = True

        self.set_camera(camera_code)

        # register the handler
        # bpy.app.handlers.render_complete.append(render_complete)

        context = utils.get_override_context()
        with bpy.context.temp_override(**context):
            bpy.ops.render.opengl(animation=True, view_context=True)
            # the reason we are not using the 'INVOKE_DEFAULT' is because render_complete handler is not working
            # with opengl render and there is no easy way to know when the render is complete or canceled.
            # If this feature fixed in the future:
            # TODO: use the 'INVOKE_DEFAULT' and use the render_complete handler
            # bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, view_context=True)

        return file_path

    @staticmethod
    def get_dcc_version():
        """Return the DCC version."""
        return bpy.app.version_string

    @staticmethod
    def get_scene_fps():
        """Return the scene FPS."""
        return utils.get_scene_fps()

    @staticmethod
    def set_scene_fps(fps_value):
        """Set the scene FPS."""
        utils.set_scene_fps(fps_value)