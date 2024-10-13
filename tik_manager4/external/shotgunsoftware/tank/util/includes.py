# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys
import posixpath
import ntpath

from .shotgun_path import ShotgunPath
from .platforms import is_windows
from ..errors import TankError


def _is_abs(path):
    """
    Check if path is absolute on any platform.

    :param str path: Path to validate.

    :returns bool: True is absolute on any platform, False otherwise.
    """
    return posixpath.isabs(path) or ntpath.isabs(path)


def _is_current_platform_abspath(path):
    """
    Check if the path is an obsolute path for the current platform.

    :param str path: Path to validate.

    :returns bool: True if absolute for this platform, False otherwise.
    """
    if is_windows():
        # ntpath likes to consider a path starting with / to be absolute,
        # but it is not!
        return ntpath.isabs(path) and not posixpath.isabs(path)
    else:
        return posixpath.isabs(path)


def resolve_include(file_name, include):
    """
    Resolve an include.

    If the path has a ~ or an environment variable, it will be resolved first.

    If the path is relative, it will be considered relative to the file that
    included it and it will be considered for any OS.

    If the path is absolute, it will only be considered to be a valid include if
    it is an absolute path for the current platform.

    Finally, the path will be sanitized to remove any extraneous slashes or slashes
    in the wrong direction.

    :param str file_name: Name of the file containing the include.
    :param str include: Include to resolve.

    :returns str: An absolute path to the resolved include or None if the file wasn't
        specified for the current platform.

    :raises TankError: Raised when the path doesn't exist.
    """
    # First resolve all environment variables and ~
    path = os.path.expanduser(os.path.expandvars(include))

    # If the path is not absolute, make it so!
    if not _is_abs(path):
        # Append it to the current file's directory.
        path = os.path.join(os.path.dirname(file_name), path)
    # We have an absolute path, so check if it is meant for this platform.
    elif not _is_current_platform_abspath(path):
        # It wasn't meant for this platform, return nothing.
        return None

    # ShotgunPath cleans up paths so that slashes are all
    # in the same direction and no doubles exist.
    path = ShotgunPath.normalize(path)

    # make sure that the paths all exist
    if not os.path.exists(path):
        raise TankError(
            "Include resolve error in '%s': '%s' resolved to '%s' which does not exist!"
            % (file_name, include, path)
        )

    return path
