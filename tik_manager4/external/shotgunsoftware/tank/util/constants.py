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
Constants relating to utility methods in tank.util
"""

# hook to get current login
CURRENT_LOGIN_HOOK_NAME = "get_current_login"

# hook to log metrics
TANK_LOG_METRICS_HOOK_NAME = "log_metrics"

# studio level core hook file name for computing the default name of a project
STUDIO_HOOK_PROJECT_NAME = "project_name.py"

# studio level core hook for specifying shotgun connection settings
STUDIO_HOOK_SG_CONNECTION_SETTINGS = "sg_connection.py"

# the storage name that is treated to be the primary storage for tank
PRIMARY_STORAGE_NAME = "primary"

# hook that is executed before a publish is registered in sg.
TANK_PUBLISH_HOOK_NAME = "before_register_publish"

# hook to decide what how folders on disk should be named
PROCESS_FOLDER_NAME_HOOK_NAME = "process_folder_name"

# a human readable explanation of the regex above - used in error messages
VALID_SG_ENTITY_NAME_EXPLANATION = (
    "letters, numbers and the characters period(.), " "dash(-) and underscore(_)"
)

# regex pattern that all folder names must validate against
VALID_SG_ENTITY_NAME_REGEX = r"^[\w\-\.]+$"

# tk instance cache of the shotgun schema
SHOTGUN_SCHEMA_CACHE_KEY = "shotgun_schema"

# tk instance cache of sg local storages
SHOTGUN_LOCAL_STORAGES_CACHE_KEY = "shotgun_local_storages"
