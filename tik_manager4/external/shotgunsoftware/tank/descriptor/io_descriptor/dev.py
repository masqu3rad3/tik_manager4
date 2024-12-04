# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .path import IODescriptorPath

from ... import LogManager

log = LogManager.get_logger(__name__)


class IODescriptorDev(IODescriptorPath):
    """
    Represents a local dev item. This item is never downloaded
    into the local storage, you interact with it directly::

        {"type": "dev", "path": "/path/to/app"}

    Optional parameters are possible::

        {"type": "dev", "path": "/path/to/app", "name": "my-app"}

        {"type": "dev",
         "linux_path": "/path/to/app",
         "windows_path": "d:\foo\bar",
         "mac_path": "/path/to/app" }

    Name is optional and if not specified will be determined based on folder path.
    If name is not specified and path is /tmp/foo/bar, the name will set to 'bar'
    """

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: descriptor dictionary describing the bundle
        :param sg_connection: Shotgun connection to associated site.
        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        :return: Descriptor instance
        """
        super(IODescriptorDev, self).__init__(
            descriptor_dict, sg_connection, bundle_type
        )

    def is_dev(self):
        """
        Returns true if this item is intended for development purposes
        """
        return True
