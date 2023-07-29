import os
from tik_manager4.dcc.main_core import DccTemplate
import subprocess

class Dcc(DccTemplate):
    formats = [".txt", ".log"]
    @staticmethod
    def save_as(file_path):
        """
        This is a mockup function to test saving a file
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format
            **extra_arguments: Compatibility arguments

        Returns:

        """
        with open(file_path, "w") as f:
            f.write("test")

        return file_path

    # TODO mix-match from Tik Manager 3

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
        subprocess.Popen([file_path], shell=True)
        pass

    @staticmethod
    def generate_thumbnail(file_path, width, height):
        """
        Grabs a thumbnail from the current scene
        Args:
            file_path: (String) File path that will be written
            width: (Int) Width of the thumbnail
            height: (Int) Height of the thumbnail

        Returns: File path of the thumbnail

        """
        # take a screenshot and save it as a thumbnail
        return None

    def get_scene_file(self):
        """Gets the current loaded scene file"""
        test_path = "C:\\Users\kutlu\\t4_test_manual_DO_NOT_USE\\Assets\\Characters\\Soldier\\bizarro\\Model\\Maya\\bizarro_Model_default_Admin_v001.txt"
        return self._normalize_file_path(test_path)



