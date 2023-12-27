"""Some cross-platform / cross-dcc related static methods"""

import os
from pathlib import Path
import platform
import subprocess

CURRENT_PLATFORM = platform.system()
def get_home_dir():
    """Get the user home directory."""
    # return str(Path().home())
    # expanduser does not always return the same result (in Maya it returns user/Documents).
    # This returns the true user folder for all platforms and dccs"""
    if platform.system() == "Windows":
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

def execute(file_path):
    if CURRENT_PLATFORM == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Linux":
        # logger.warning("Linux execution not yet implemented")
        subprocess.Popen(["xdg-open", file_path])
    else:
        subprocess.Popen(["open", file_path])
