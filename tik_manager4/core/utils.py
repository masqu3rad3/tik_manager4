"""Some cross-platform / cross-dcc related static methods"""

import os
from pathlib import Path
import platform
import subprocess

CURRENT_PLATFORM = platform.system()
def get_home_dir():
    """Get the user home directory."""
    # expanduser does not always return the same result (in Maya it returns user/Documents).
    # This returns the true user folder for all platforms and dccs"""
    if CURRENT_PLATFORM == "Windows":
        return os.path.normpath(os.getenv("USERPROFILE"))
    else:
        return os.path.normpath(os.getenv("HOME"))

def apply_stylesheet(file_path, widget):
    """reads and applies the qss file to the widget"""

    if Path(file_path).is_file():
        with open(file_path, "r") as fh:
            widget.setStyleSheet(fh.read())
        return True
    else:
        return False

def execute(file_path, executable=None):
    """Execute a file.

    Args:
        file_path (str): The file path to execute.
        executable (str, optional): The executable to use. If not
            defined the system defined one will be used. Defaults to None.
            Flags can be passed at the eng of the string.
            e.g. "path/to/file -flag1 -flag2".
    """
    if executable:
        # validate the existence
        if not Path(executable).is_file():
            raise ValueError("The executable does not exist. {}".format(executable))
        # subprocess.Popen(executable.split(" ") + [file_path], shell=True)
        subprocess.Popen([executable, file_path], shell=True)
    else:
        if CURRENT_PLATFORM == "Windows":
            os.startfile(file_path)
        elif CURRENT_PLATFORM == "Linux":
            # logger.warning("Linux execution not yet implemented")
            subprocess.Popen(["xdg-open", file_path])
        else:
            subprocess.Popen(["open", file_path])
