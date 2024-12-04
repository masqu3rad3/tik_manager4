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
Legacy handling of descriptors for the PTR desktop app.

This code may be removed at some point in the future.
"""

# import methods to ensure that older version of the desktop engine
# will function correctly - the code calls these internal methods
from ..util.version import is_version_newer, is_version_older
