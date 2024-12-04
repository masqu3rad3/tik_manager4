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


class TankDevDescriptor(object):
    """
    Stub class to make sure that the desktop startup logic can
    execute the following like of code (where it accesses
    toolkit internals)::

        if isinstance(current_desc, sgtk.deploy.dev_descriptor.TankDevDescriptor):
            logger.info("Desktop startup using a dev descriptor, skipping update...")
            return False

    """

    pass
