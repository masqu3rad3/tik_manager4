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
Folder related exceptions.
"""


class EntityLinkTypeMismatch(Exception):
    r"""
    Exception raised to indicate that a shotgun
    entity link is incorrectly typed
    and therefore cannot be traversed.

    For example, imagine there is an entity Workspace which
    can link to both shots and assets via an sg_entity link.

    you then have two configuration branches:

    project->asset->workspace
       \-->shot->workspace

    you now have a workspace entity with id 123 which links to an asset.

    If you run extract_shotgun_data_upwards method for id 123
    and start from the folder object in the shot branch, the link
    will be mismatching since the sg_entity for id 123 points at an
    asset not a shot. In those cases, this exception is being raised
    from inside  extract_shotgun_data_upwards.
    """
