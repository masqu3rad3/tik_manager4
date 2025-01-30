"""Cross-platform utility functions."""

import os
import logging
from pathlib import Path
import shutil
import platform
import subprocess
import re
import unicodedata

from tik_manager4.external import fileseq

CURRENT_PLATFORM = platform.system()

LOG = logging.getLogger(__name__)

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
    # check if file exists
    path_obj = Path(file_path)
    if not path_obj.exists():
        # may it be a sequential file?
        if len(path_obj.suffixes) < 2:
            raise FileNotFoundError(
                "The file does not exist. {}".format(file_path))
        pattern = path_obj.as_posix().replace(path_obj.suffixes[0], ".@")
        seq = fileseq.findSequenceOnDisk(pattern)
        if not seq:
            raise FileNotFoundError(
                "The file does not exist. {}".format(file_path))
        file_path = seq.index(0)

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

# def move(source, target, force=True):
#     """Move the source file or folder to the target location."""
#     if Path(source).is_file():
#         copy_function = shutil.copy2
#     else:
#         copy_function = shutil.copytree
#
#     Path(target).parent.mkdir(parents=True, exist_ok=True)
#     shutil.move(source, target, copy_function=copy_function)

def move(source, target, force=True, raise_error=False):
    """Move the source file or folder to the target location.

    If force is True, any existing file or folder at the target location
    will be removed before the move operation.
    """
    source = Path(source)
    if not source.exists():
        if raise_error:
            raise FileNotFoundError(f"Source file or folder does not exist: {source}")
        return False, f"Source file or folder does not exist: {source}"
    target = Path(target)

    # If force is True and the target exists, remove it
    if force and target.exists():
        ret, msg = delete(target)
        if not ret:
            return False, f"Error deleting target: {msg}"

    # Ensure the target's parent directory exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # Perform the move operation
    shutil.move(str(source), str(target))
    return True, f"{source} moved to {target}."

def delete(file_or_folder):
    """Delete the file or folder."""
    try:
        if Path(file_or_folder).is_file() or Path(file_or_folder).is_symlink():
            Path(file_or_folder).unlink()
        elif Path(file_or_folder).is_dir():
            shutil.rmtree(file_or_folder)
    except PermissionError as e:
        ret, msg = write_unprotect(file_or_folder)
        if not ret:
            return False, f"Error removing write protection: {file_or_folder}"
        delete(file_or_folder)
    return True, f"{file_or_folder} deleted."

def write_protect(file_or_folder):
    """Write protect the file or folder."""
    path = Path(file_or_folder)
    file_list = []
    if path.is_file():
        file_list.append(path)
    elif path.is_dir():
        for _file in path.rglob("*"):
            file_list.append(_file)
    for _file in file_list:
        try:
            _file.chmod(0o444)
            return True, "Write protection applied."
        except Exception as e:  # pylint: disable=broad-except
            LOG.error(f"Error applying write protection: {e}")
            return False, f"Error applying write protection: {e}"

def write_unprotect(file_or_folder):
    """Write unprotect the file or folder."""
    path = Path(file_or_folder)
    file_list = []
    if path.is_file():
        file_list.append(path)
    elif path.is_dir():
        for _file in path.rglob("*"):
            file_list.append(_file)
    for _file in file_list:
        try:
            _file.chmod(0o777)
            return True, "Write protection removed."
        except Exception as e:  # pylint: disable=broad-except
            LOG.error(f"Error removing write protection: {e}")
            return False, f"Error removing write protection: {e}"