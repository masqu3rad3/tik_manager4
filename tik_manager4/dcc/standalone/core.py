import os
from tik_manager4.dcc.template import DccTemplate


class Dcc(DccTemplate):

    @staticmethod
    def save_as(file_path, format=None, **extra_arguments):
        """
        This is a mockup function to test saving a file
        Args:
            file_path: (String) File path that will be written
            format: (String) File format
            **extra_arguments: Compatibility arguments

        Returns:

        """
        with open(file_path, "w") as f:
            f.write("test")

    # TODO mix-match from Tik Manager 3