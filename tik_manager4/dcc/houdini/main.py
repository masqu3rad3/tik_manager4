from pathlib import Path
import os
import logging

import hou
import toolutils

# from tik_manager4.ui.Qt import QtWidgets

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.houdini import validate
from tik_manager4.dcc.houdini import extract
from tik_manager4.dcc.houdini import ingest


LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    name = "Houdini"
    formats = [".hip", ".hiplc", ".hipnc"]
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

        Returns: (String) File path

        """
        if hou.isApprentice():
            file_path = Path(file_path).with_suffix(".hipnc")
        hou.hipFile.save(file_name=str(file_path))
        return str(file_path)

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
        self._set_env_variable("HIP", str(Path(file_path).parent))

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
        cameras = hou.nodeType(hou.objNodeTypeCategory(), "cam").instances()
        _dict = {}
        for cam in cameras:
            _dict[cam.name()] = cam.path()
        # add the perspective as an option
        _dict["persp"] = ""
        return _dict

    @staticmethod
    def get_current_camera():
        """
        Return the current camera in the scene.
        Returns: (String) Camera name (String), Node path (String)
        """
        _camera = (
            hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().camera()
        )
        if not _camera:
            return "persp", ""
        return _camera.name(), _camera.path()

    @staticmethod
    def generate_preview(name, folder, camera_code, resolution, range, settings=None):
        """
        Create a preview from the current scene
        Args:
            name: (String) Name of the preview
            folder: (String) Folder to save the preview
            camera_code: (String) Camera code. In Houdini, this is the node path
            resolution: (list) Resolution of the preview
            range: (list) Range of the preview
            settings: (dict) Global Settings dictionary
        """

        extension = "jpg"

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

        scene_view = toolutils.sceneViewer()
        viewport = scene_view.curViewport()

        if camera_code != "":  # if camera is not perspective
            hou.GeometryViewport.setCamera(viewport, camera_code)

        file_path = Path(folder) / f"{name}.$F4.{extension}"

        flip_options = scene_view.flipbookSettings().stash()

        flip_options.output(file_path)
        flip_options.rameRange((range[0], range[1]))
        flip_options.outputToMPlay(not settings["PostConversion"])
        flip_options.useResolution(True)
        flip_options.resolution((resolution[0], resolution[1]))
        scene_view.flipbook(viewport, flip_options)

        return file_path

    @staticmethod
    def get_dcc_version():
        """Return the DCC major version."""
        return hou.applicationVersion()[0]

    @staticmethod
    def get_scene_fps():
        """Return the current FPS value set by DCC. None if not supported."""
        return hou.fps()

    def set_scene_fps(self, fps_value):
        """
        Set the FPS value in DCC if supported.
        Args:
            fps_value: (integer) fps value

        Returns: None

        """
        range = self.get_ranges()
        hou.setFps(fps_value)
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
