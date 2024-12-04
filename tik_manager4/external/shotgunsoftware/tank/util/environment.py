# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Helper methods that do environment management
"""

import os
from .platforms import is_windows


def append_path_to_env_var(env_var_name, path):
    """
    Append the path to the given environment variable.
    Creates the env var if it doesn't exist already.
    will concatenate paths using : on linux and ; on windows
    """

    return _add_path_to_env_var(env_var_name, path, prepend=False)


def prepend_path_to_env_var(env_var_name, path):
    """
    Prepend the path to the given environment variable.
    Creates the env var if it doesn't exist already.
    will concatenate paths using : on linux and ; on windows
    """

    return _add_path_to_env_var(env_var_name, path, prepend=True)


def _add_path_to_env_var(env_var_name, path, prepend=False):
    """
    Append or prepend the path to the given environment variable.
    Creates the env var if it doesn't exist already.
    will concatenate paths using : on linux and ; on windows
    """

    if is_windows():
        env_var_sep = ";"
    else:
        env_var_sep = ":"

    paths = os.environ.get(env_var_name, "").split(env_var_sep)
    # clean up empty entries
    paths = [x for x in paths if x != ""]
    # Do not add path if it already exists in the list
    if path not in paths:
        if prepend:
            paths.insert(0, path)
        else:
            paths.append(path)
    # and put it back
    os.environ[env_var_name] = env_var_sep.join(paths)
