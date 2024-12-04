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

from ..descriptor import create_descriptor, Descriptor
from ..util import shotgun


class AppDescriptor(object):
    """
    Kept for backwards compatibility reasons for get_from_location_and_paths()
    """

    APP, ENGINE, FRAMEWORK = range(3)


def get_from_location_and_paths(
    app_or_engine, pc_path, bundle_install_path, location_dict
):
    """
    Factory method.

    LEGACY - Use create_descriptor instead. This is itended only for
    older versions of the PTR desktop app.

    :param app_or_engine: Either AppDescriptor.APP ENGINE CORE or FRAMEWORK (as defined above)
    :param pc_path: Path to the root of the pipeline configuration.
                    Legacy parameter and no longer used. This value will be ignored.
    :param bundle_install_path: Path to the root of the apps, frameworks and engines bundles.
    :param location_dict: A tank location dict (now known as a descriptor dict)
    :returns: an AppDescriptor object
    """
    sg_connection = shotgun.get_sg_connection()

    # cast legacy enums to use new form
    enums = {
        AppDescriptor.APP: Descriptor.APP,
        AppDescriptor.ENGINE: Descriptor.ENGINE,
        AppDescriptor.FRAMEWORK: Descriptor.FRAMEWORK,
    }
    new_descriptor_type = enums[app_or_engine]

    return create_descriptor(
        sg_connection, new_descriptor_type, location_dict, bundle_install_path
    )
