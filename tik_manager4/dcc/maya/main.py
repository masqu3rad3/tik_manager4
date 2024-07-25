"""Main module for Maya DCC integration."""

from pathlib import Path
import logging
import platform

from maya import cmds
from maya import mel
import maya.OpenMaya as om
from maya import OpenMayaUI as omui

from tik_manager4.ui.Qt import QtWidgets, QtCompat
from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.maya import utils
from tik_manager4.dcc.maya import panels
from tik_manager4.dcc.maya import validate
from tik_manager4.dcc.maya import extract
from tik_manager4.dcc.maya import ingest

LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    """Maya DCC class."""

    name = "Maya"
    formats = [".ma", ".mb"]
    preview_enabled = True  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    @staticmethod
    def get_main_window():
        """Get the memory adress of the main window to connect Qt dialog to it.
        Returns:
            (long or int) Memory Adress
        """
        try:
            win = omui.MQtUtil_mainWindow()
        except AttributeError:  # Maya 2025 / Qt 6
            win = omui.MQtUtil.mainWindow()
        ptr = QtCompat.wrapInstance(int(win), QtWidgets.QMainWindow)
        return ptr

    @staticmethod
    def save_scene():
        """Saves the current file"""
        cmds.file(save=True)

    @staticmethod
    def save_as(file_path):
        """Save the current scene as a new file.
        Args:
            file_path (str): The file path to save the scene to.
        Returns:
            (str) The file path that the scene was saved to.
        """
        extension = Path(file_path).suffix
        file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        cmds.file(rename=file_path)
        cmds.file(save=True, type=file_format)
        return file_path

    @staticmethod
    def save_prompt():
        """Pop up the save prompt."""
        cmds.SaveScene()
        return True  # this is important or else will be an indefinite loop

    @staticmethod
    def open(file_path, force=True, **_extra_arguments):
        """Open the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **_extra_arguments: Compatibility arguments for other DCCs

        Returns: None
        """
        cmds.file(file_path, open=True, force=force)

    @staticmethod
    def get_ranges():
        """Get the viewport ranges."""
        return utils.get_ranges()

    @staticmethod
    def set_ranges(range_list):
        """Set the timeline ranges."""
        utils.set_ranges(range_list)

    @staticmethod
    def set_project(file_path):
        """
        Sets the project to the given path
        Args:
            file_path: (String) Path to the project folder

        Returns: None

        """
        cmds.workspace(file_path, openWorkspace=True)

    @staticmethod
    def is_modified():
        """Returns True if the scene has unsaved changes"""
        # an empty string (not saved) should return False IF the scene is empty
        # not having any DAG objects in the scene doesnt necessarily mean the scene is empty
        # but we will assume that for now.
        default_dag_nodes = [
            "persp",
            "perspShape",
            "top",
            "topShape",
            "front",
            "frontShape",
            "side",
            "sideShape",
        ]
        if cmds.ls(dag=True) == default_dag_nodes:
            return False
        return cmds.file(query=True, modified=True)

    @staticmethod
    def get_scene_file():
        """Get the current scene file."""
        # This logic is borrowed from the pymel implementation of sceneName().

        # Get the name for untitled files in Maya.
        untitled_file_name = mel.eval("untitledFileName()")
        path = om.MFileIO.currentFile()

        file_name = Path(path).name
        # Don't just use cmds.file(q=1, sceneName=1)
        # because it was sometimes returning an empty string,
        # even when there was a valid file
        # Check both the OpenMaya.MFileIO.currentFile() and
        # the cmds.file(q=1, sceneName=1)
        # so as to be sure that no file is open.
        # This should mean that if someone does have
        # a file open and it's named after the untitledFileName we should still
        # be able to return the path.
        if (
            file_name.startswith(untitled_file_name)
            and cmds.file(q=1, sceneName=1) == ""
        ):
            return ""
        return path

    @staticmethod
    def get_current_frame():
        """Return current frame in timeline.
        If dcc does not have a timeline, returns None.
        """
        return cmds.currentTime(query=True)

    def generate_thumbnail(self, file_path, width, height):
        """
        Grabs a thumbnail from the current scene
        Args:
            file_path: (String) File path to save the thumbnail
            width: (Int) Width of the thumbnail
            height: (Int) Height of the thumbnail

        Returns: None

        """

        # create a thumbnail using playblast
        frame = self.get_current_frame()
        store = cmds.getAttr("defaultRenderGlobals.imageFormat")
        cmds.setAttr(
            "defaultRenderGlobals.imageFormat", 8
        )  # This is the value for jpeg
        cmds.playblast(
            completeFilename=file_path,
            forceOverwrite=True,
            format="image",
            width=width,
            height=height,
            showOrnaments=False,
            frame=[frame],
            viewer=False,
            percent=100,
        )
        cmds.setAttr("defaultRenderGlobals.imageFormat", store)  # take it back
        return file_path

    @staticmethod
    def get_scene_fps():
        """Return the current FPS value set by DCC. None if not supported."""
        return utils.get_scene_fps()

    @staticmethod
    def set_scene_fps(fps_value):
        """
        Set the FPS value in DCC if supported.
        Args:
            fps_value: (integer) fps value

        Returns: None

        """
        utils.set_scene_fps(fps_value)

    @staticmethod
    def get_scene_cameras():
        """
        Return a dictionary of all the cameras in the scene where key is the camera name and value is the camera uuid.
        """
        all_cameras = cmds.ls(type="camera")
        _dict = {}
        for cam in all_cameras:
            _dict[cmds.listRelatives(cam, parent=True)[0]] = cmds.ls(cam, uuid=True)[0]
        return _dict

    @staticmethod
    def get_current_camera():
        """Get the current camera and its uuid."""
        camera = cmds.modelPanel(cmds.getPanel(withFocus=True), query=True, camera=True)
        return camera, cmds.ls(camera, uuid=True)[0]

    @staticmethod
    def generate_preview(name, folder, camera_code, resolution, range, settings=None):
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

        playback_slider = mel.eval("$tmpVar=$gPlayBackSlider")
        active_sound = cmds.timeControl(playback_slider, q=True, sound=True)

        if platform.system() == "Windows":
            output_format = "avi"
            output_codec = "none"
            extension = "avi"
        else:
            output_format = "qt"
            output_codec = "jpg"
            extension = "mov"

        # Create pb panel and adjust it due to settings
        _camera = cmds.ls(camera_code)[0]
        # we need to make sure that we are getting the transform of the camera
        # not the shape node. This is for a workaround for the panel manager.
        if cmds.objectType(_camera) == "camera":
            _camera = cmds.listRelatives(_camera, parent=True, type="transform")[0]

        pb_panel = panels.PanelManager(_camera, resolution, inherit=True)

        if not settings.get("ViewportAsItIs"):
            pb_panel.display_field_chart = settings.get("DisplayFieldChart", False)
            pb_panel.display_gate_mask = settings.get("DisplayGateMask", False)
            pb_panel.display_film_gate = settings.get("DisplayFilmGate", False)
            pb_panel.display_film_origin = settings.get("DisplayFilmOrigin", False)
            pb_panel.display_film_pivot = settings.get("DisplayFilmPivot", False)
            pb_panel.display_resolution = settings.get("DisplayResolution", False)
            pb_panel.display_safe_action = settings.get("DisplaySafeAction", False)
            pb_panel.display_safe_title = settings.get("DisplaySafeTitle", False)

            pb_panel.all_objects = not settings.get("PolygonOnly", True)
            pb_panel.display_appearance = settings.get(
                "DisplayAppearance", "smoothShaded"
            )
            pb_panel.display_textures = settings.get("DisplayTextures", True)
            pb_panel.grid = settings.get("ShowGrid", False)
            pb_panel.use_default_material = settings.get("UseDefaultMaterial", False)
            pb_panel.polymeshes = True
            pb_panel.image_plane = True

        if not settings.get("HudsAsItIs"):
            pb_panel.hud = False

        _output = cmds.playblast(
            format=output_format,
            # sequenceTime=sequenceTime,
            filename=str(Path(folder) / name),
            widthHeight=resolution,
            percent=settings.get("Percent", 100),
            quality=settings.get("Quality", 100),
            compression=output_codec,
            sound=active_sound,
            # useTraxSounds=True,
            viewer=False,
            offScreen=True,
            offScreenViewportUpdate=True,
            activeEditor=False,
            editorPanelName=pb_panel.panel,
            startTime=range[0],
            endTime=range[1],
        )

        final_clip = f"{_output}.{extension}"
        pb_panel.kill()
        return final_clip

    @staticmethod
    def get_dcc_version():
        """Return the DCC major version."""
        return str(cmds.about(query=True, majorVersion=True))
