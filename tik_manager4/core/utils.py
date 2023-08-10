"""Some cross-platform / cross-dcc related static methods"""

import os
import platform


def get_home_dir():
    """Get the user home directory.
    expanduser does not always return the same result
    (in Maya it returns user/Documents). This returns the true user folder for all
    platforms and dccs.
    """
    if platform.system() == "Windows":
        return os.path.normpath(os.getenv("USERPROFILE"))
    else:
        return os.path.normpath(os.getenv("HOME"))


def apply_stylesheet(file_path, widget):
    """reads and applies the qss file to the widget"""

    if os.path.isfile(file_path):
        with open(file_path, "r") as fh:
            widget.setStyleSheet(fh.read())
        return True
    else:
        return False
