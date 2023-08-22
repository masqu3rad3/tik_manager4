import os
from maya import cmds
from maya import mel
import maya.OpenMaya as om
from tik_manager4.ui.Qt import QtWidgets, QtCompat
from maya import OpenMayaUI as omui

from tik_manager4.dcc.main_core import DccTemplate


class Dcc(DccTemplate):
    formats = [".ma", ".mb"]

    @staticmethod
    def get_main_window():
        """
        Gets the memory adress of the main window to connect Qt dialog to it.
        Returns:
            (long or int) Memory Adress
        """
        win = omui.MQtUtil_mainWindow()
        # dropping the py2 compatibility
        ptr = QtCompat.wrapInstance(int(win), QtWidgets.QMainWindow)
        return ptr

    def new_scene(self, force=True, fps=None):
        """
        Opens a new scene

        Args:
            force: (Bool) If true, any unsaved changes will be lost. Else throw an error
            fps: (Int) Accepts integer fps values.

        Returns: None

        """
        cmds.file(newFile=True, force=force)
        if fps:
            fps_dict = {
                15: "game",
                24: "film",
                25: "pal",
                30: "ntsc",
                48: "show",
                50: "palf",
                60: "ntscf",
            }
            ranges = self.get_ranges()
            cmds.currentUnit(time=fps_dict[fps])
            self.set_ranges(ranges)
            cmds.currentTime(1)

    @staticmethod
    def save_scene():
        """Saves the current file"""
        cmds.file(save=True)

    @staticmethod
    def save_as(file_path):
        """
        Saves the file to the given path
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format
            **extra_arguments: Compatibility arguments

        Returns:

        """
        extension = os.path.splitext(file_path)[1]
        file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        cmds.file(rename=file_path)
        cmds.file(save=True, type=file_format)

    @staticmethod
    def open(file_path, force=True, **extra_arguments):
        """
        Opens the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **extra_arguments: Compatibility arguments for other DCCs

        Returns: None

        """
        cmds.file(file_path, open=True, force=force)

    @staticmethod
    def reference(file_path, namespace):
        """
        References a file
        Args:
            file_path: (String) the file path to be referenced
            namespace: (String) namespace for uniqueness

        Returns: (List) Referenced nodes

        """
        cmds.file(
            Dcc._normalize_file_path(file_path),
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=namespace,
        )
        # TODO return referenced nodes

    @staticmethod
    def import_file(file_path, **extra_arguments):
        """
        Imports the given file to the current scene
        Args:
            file_path: (String) File path to be imported
            **extra_arguments: Compatibility arguments

        Returns: (List) Imported nodes

        """
        cmds.file(file_path, i=True)
        # TODO return imported nodes

    @staticmethod
    def get_ranges():
        """
        Get the viewport ranges.
        Returns: (list) [<absolute range start>, <user range start>, <user range end>,
        <absolute range end>
        """
        r_ast = cmds.playbackOptions(query=True, animationStartTime=True)
        r_min = cmds.playbackOptions(query=True, minTime=True)
        r_max = cmds.playbackOptions(query=True, maxTime=True)
        r_aet = cmds.playbackOptions(query=True, animationEndTime=True)
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
        cmds.playbackOptions(
            animationStartTime=range_list[0],
            minTime=range_list[1],
            maxTime=range_list[2],
            animationEndTime=range_list[3],
        )

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
        return cmds.file(query=True, modified=True)

    @staticmethod
    def get_scene_file():
        """
        Returns the path to the current scene.
        :return: str
        """
        # This logic is borrowed from the pymel implementation of sceneName().

        # Get the name for untitled files in Maya.
        untitled_file_name = mel.eval("untitledFileName()")
        path = om.MFileIO.currentFile()

        file_name = os.path.basename(path)
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
            width=221,
            height=124,
            showOrnaments=False,
            frame=[frame],
            viewer=False,
            percent=100,
        )
        cmds.setAttr("defaultRenderGlobals.imageFormat", store)  # take it back

    @staticmethod
    def get_scene_cameras():
        """
        Return all the cameras in the scene.
        Returns: (list) List of camera names
        """
        return [cmds.listRelatives(x, parent=True)[0] for x in cmds.ls(type="camera")]


    @staticmethod
    def generate_preview(name, folder, camera=None, resolution=None, settings_file=None):
        """
        Create a preview from the current scene
        Args:
            file_path: (String) File path to save the preview

        Returns: (String) File path of the preview

        """
        pass