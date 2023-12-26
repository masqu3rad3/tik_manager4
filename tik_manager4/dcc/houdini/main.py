from pathlib import Path
import os
import logging

import hou

# from tik_manager4.ui.Qt import QtWidgets

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.max import validate
from tik_manager4.dcc.max import extract
from tik_manager4.dcc.max import ingest


LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    name = "Houdini"
    formats = [".hip", ".hiplc"]
    preview_enabled = True  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    @staticmethod
    def get_main_window():
        """Get the main window."""
        return hou.qt.mainWindow()

    @staticmethod
    def save_scene():
        """Save the current scene."""
        hou.hipFile.save()

    @staticmethod
    def save_as(file_path):
        """
        Saves the file to the given path
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format

        Returns:

        """
        hou.hipFile.save(file_name=file_path)

    def open(self, file_path, force=True, **extra_arguments):
        """
        Opens the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **extra_arguments: Compatibility arguments for other DCCs

        Returns: None

        """
        hou.hipFile.load(
            file_path, suppress_save_prompt=force, ignore_load_warnings=False
        )
        self._set_env_variable("HIP", Path(file_path).parent)

    @staticmethod
    def get_ranges():
        """Get the viewport ranges."""
        r_ast = int(hou.playbar.frameRange()[0])
        r_min = int(hou.playbar.playbackRange()[0])
        r_max = int(hou.playbar.playbackRange()[1])
        r_aet = int(hou.playbar.frameRange()[1])
        return [r_ast, r_min, r_max, r_aet]

    @staticmethod
    def set_ranges(range_list):
        """
        Set the timeline ranges.

        Args:
            range_list: list of ranges as [<animation start>, <user min>, <user max>,
                                            <animation end>]

        Returns: None

        """
        hou.playbar.setFrameRange(range_list[0], range_list[3])
        hou.playbar.setPlaybackRange(range_list[1], range_list[2])

    @staticmethod
    def is_modified():
        """Check if the scene has unsaved changes."""
        return hou.hipFile.hasUnsavedChanges()

    @staticmethod
    def get_scene_file():
        """Get the current scene file."""
        s_path = Path(hou.hipFile.path())
        nice_name = s_path.name
        if nice_name == "untitled":
            return ""
        return str(s_path)

    @staticmethod
    def get_current_frame():
        """Return current frame in timeline.
        If dcc does not have a timeline, returns None.
        """
        return hou.frame()

    def generate_thumbnail(self, file_path, width, height):
        """
        Grabs a thumbnail from the current scene
        Args:
            file_path: (String) File path to save the thumbnail
            width: (Int) Width of the thumbnail
            height: (Int) Height of the thumbnail

        Returns: None

        """

        frame = self.get_current_frame()
        current_desktop = hou.ui.curDesktop()
        scene = current_desktop.paneTabOfType(hou.paneTabType.SceneViewer)
        flip_options = scene.flipbookSettings().stash()
        flip_options.frameRange((frame, frame))
        flip_options.outputToMPlay(False)
        flip_options.output(file_path)
        flip_options.useResolution(True)
        flip_options.resolution((width, height))
        scene.flipbook(scene.curViewport(), flip_options)

        return file_path

    @staticmethod
    def get_scene_cameras():
        """
        Return all the cameras in the scene.
        Returns: (list) List of camera names
        """
        # Get all nodes in the scene
        all_nodes = hou.node("/").allSubChildren()
        # Filter nodes to get only cameras
        cameras = [node for node in all_nodes if node.type().name() == "cam"]
        return cameras

    @staticmethod
    def generate_preview(name, folder, camera, resolution, range, settings=None):
        """
        Create a preview from the current scene
        Args:
            file_path: (String) File path to save the preview

        Returns: (String) File path of the preview

        """

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

        extension = "avi"

        # get the current values
        original_values = {
            "width": rt.renderWidth,
            "height": rt.renderHeight,
            "selection": rt.getCurrentSelection(),
        }

        # change the render settings temporarily
        rt.renderWidth = resolution[0]
        rt.renderHeight = resolution[1]

        display_geometry = bool(settings["PolygonOnly"])
        display_shapes = not bool(settings["PolygonOnly"])
        display_lights = not bool(settings["PolygonOnly"])
        display_cameras = not bool(settings["PolygonOnly"])
        display_helpers = not bool(settings["PolygonOnly"])
        display_particles = not bool(settings["PolygonOnly"])
        display_bones = not bool(settings["PolygonOnly"])
        display_grid = bool(settings["ShowGrid"])
        display_frame_nums = bool(settings["ShowFrameNumber"])
        percent_size = settings["Percent"]
        render_level = (
            rt.execute("#litwireframe")
            if settings["WireOnShaded"]
            else rt.execute("#smoothhighlights")
        )
        if settings["ClearSelection"]:
            rt.clearSelection()

        file_path = Path(folder) / f"{name}.{extension}"

        rt.createPreview(
            filename=file_path,
            percentSize=percent_size,
            dspGeometry=display_geometry,
            dspShapes=display_shapes,
            dspLights=display_lights,
            dspCameras=display_cameras,
            dspHelpers=display_helpers,
            dspParticles=display_particles,
            dspBones=display_bones,
            dspGrid=display_grid,
            dspFrameNums=display_frame_nums,
            rndLevel=render_level,
        )

        # restore the original values
        rt.renderWidth = original_values["width"]
        rt.renderHeight = original_values["height"]
        rt.select(original_values["selection"])

        return file_path

    @staticmethod
    def get_dcc_version():
        """Return the DCC major version."""
        return rt.maxversion()[0]

    @staticmethod
    def get_scene_fps():
        """Return the current FPS value set by DCC. None if not supported."""
        return rt.framerate

    def set_scene_fps(self, fps_value):
        """
        Set the FPS value in DCC if supported.
        Args:
            fps_value: (integer) fps value

        Returns: None

        """
        range = self.get_ranges()
        rt.framerate = fps_value
        self.set_ranges(range)

    def _set_env_variable(self, var, value):
        """sets environment var
        Args:
            var: (String) Environment variable name
            value: (String) Value to set
        """
        os.environ[var] = value
        try:
            hou.allowEnvironmentVariableToOverwriteVariable(var, True)
        except AttributeError:
            # should be Houdini 12
            hou.allowEnvironmentToOverwriteVariable(var, True)

        value = value.replace("\\", "/")
        hscript_command = "set -g %s = '%s'" % (var, value)

        hou.hscript(str(hscript_command))
