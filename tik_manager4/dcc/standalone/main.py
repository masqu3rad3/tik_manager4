from tik_manager4.dcc.main_core import MainCore
import subprocess


class Dcc(MainCore):
    formats = [".txt", ".log"]
    preview_enabled = False

    @staticmethod
    def save_as(file_path):
        """Save (mockup) the file.
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format
            **extra_arguments: Compatibility arguments

        Returns:

        """
        with open(file_path, "w") as f:
            f.write("test")

        return file_path

    @staticmethod
    def open(file_path, force=True, **extra_arguments):
        """Open the given file path.
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **extra_arguments: Compatibility arguments for other DCCs

        Returns: None

        """
        subprocess.Popen([file_path], shell=True)
