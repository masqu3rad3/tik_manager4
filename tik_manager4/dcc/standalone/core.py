import os
from tik_manager4.dcc.template import DccTemplate


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



