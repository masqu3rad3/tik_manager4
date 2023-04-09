import os
from maya import cmds, mel

from tik_manager4.dcc.template import DccTemplate


class Dcc(DccTemplate):
    def new_scene(self, force=True, fps=None):
        """
        Opens a new scene

        Args:
            force: (Bool) If true, any unsaved changes will be lost. Else throw an error
            fps: (Int) Accepts integer fps values.

        Returns: None

        """
        cmds.file(new=True, f=force)
        if fps:
            fps_dict = {15: "game",
                       24: "film",
                       25: "pal",
                       30: "ntsc",
                       48: "show",
                       50: "palf",
                       60: "ntscf"}
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
        cmds.file(file_path, o=True, force=force)

    @staticmethod
    def reference(file_path, namespace):
        """
        References a file
        Args:
            file_path: (String) the file path to be referenced
            namespace: (String) namespace for uniqueness

        Returns: (List) Referenced nodes

        """
        cmds.file(Dcc._normalize_file_path(file_path), reference=True, gl=True, mergeNamespacesOnClash=False,
                  namespace=namespace)
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
        Gets the viewport ranges
        Returns: (list) [<absolute range start>, <user range start>, <user range end>, <absolute range end>
        """
        r_ast = cmds.playbackOptions(q=True, ast=True)
        r_min = cmds.playbackOptions(q=True, min=True)
        r_max = cmds.playbackOptions(q=True, max=True)
        r_aet = cmds.playbackOptions(q=True, aet=True)
        return [r_ast, r_min, r_max, r_aet]

    @staticmethod
    def set_ranges(range_list):
        """
        sets the timeline ranges

        Args:
            range_list: list of ranges as [<animation start>, <user min>, <user max>, <animation end>]

        Returns: None

        """
        cmds.playbackOptions(ast=range_list[0], min=range_list[1], max=range_list[2], aet=range_list[3])

    @staticmethod
    def is_modified():
        """Returns True if the scene has unsaved changes"""
        return cmds.file(q=True, modified=True)
