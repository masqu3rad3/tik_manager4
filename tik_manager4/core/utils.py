"""Cross-platform utility functions."""

import os
from pathlib import Path
import platform
import subprocess
import re
import unicodedata

CURRENT_PLATFORM = platform.system()


def get_home_dir():
    """Get the user home directory."""
    # expanduser does not always return the same result (in Maya it returns user/Documents).
    # This returns the true user folder for all platforms and dccs"""
    if CURRENT_PLATFORM == "Windows":
        return os.path.normpath(os.getenv("USERPROFILE"))
    return os.path.normpath(os.getenv("HOME"))


def apply_stylesheet(file_path, widget):
    """Read and apply the qss file to the given widget.

    Args:
        file_path (str): The file path to the qss file.
        widget (QtWidgets.QWidget): The widget to apply the stylesheet to.

    Returns:
        bool: True if the file exists and applied, False otherwise.
    """

    if Path(file_path).is_file():
        with open(file_path, "r") as _file:
            widget.setStyleSheet(_file.read())
        return True
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
        subprocess.Popen([executable, file_path], shell=True)
    else:
        if CURRENT_PLATFORM == "Windows":
            os.startfile(file_path)
        elif CURRENT_PLATFORM == "Linux":
            # logger.warning("Linux execution not yet implemented")
            subprocess.Popen(["xdg-open", file_path])
        else:
            subprocess.Popen(["open", file_path])

def sanitize_text(text, allow_spaces=False):
    """
    Sanitizes the given text by removing localized characters, replacing spaces
    with underscores, and removing or replacing illegal characters based on the pattern.
    """

    # Normalize and remove special/localized characters
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c if unicodedata.category(c) != "Mn" else "" for c in text)

    # Replace spaces with underscores if spaces are not allowed
    if not allow_spaces:
        text = text.replace(" ", "_")

    # Define pattern to match allowed characters and remove illegal ones
    pattern = r"[^A-Za-z0-9A_-]"
    sanitized_text = re.sub(pattern, "", text)

    return sanitized_text
