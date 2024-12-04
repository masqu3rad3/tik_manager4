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
All custom exceptions that Tank emits are defined here.
"""


class TankError(Exception):
    """
    Top level exception for all toolkit-core level runtime errors
    """


class TankInitError(TankError):
    """
    Exception indicating initialization failure.
    """


class TankUnreadableFileError(TankError):
    """
    Exception that indicates that a required file can't be read from disk.
    """


class TankFileDoesNotExistError(TankUnreadableFileError):
    """
    Exception that indicates that a required file does not exist.
    """


class TankNoDefaultValueError(TankError):
    """
    Exception that can be raised when a default value is required but none is found.
    """


class TankHookMethodDoesNotExistError(TankError):
    """
    Exception that indicates that a called method does not exist in the hook.
    """


class TankInvalidCoreLocationError(TankError):
    """
    Exception that indicates the core location file contained an invalid path.
    """


class TankNotPipelineConfigurationError(TankError):
    """
    Exception that indicates that a folder doesn't contain a pipeline configuration.
    """


class TankErrorProjectIsSetup(TankError):
    """
    Exception that indicates that a project already has a toolkit name but no pipeline configuration.
    """

    def __init__(self):
        """
        Include error message
        """
        super(TankErrorProjectIsSetup, self).__init__(
            "You are trying to set up a project which has already been set up. "
            "If you want to do this, make sure to set the force parameter."
        )


class TankContextDeserializationError(TankError):
    """
    Exception that indicates that something went wrong while deserializating a context.
    """


class TankMultipleMatchingTemplatesError(TankError):
    """
    Exception that indicates that a path matches multiple templates.
    """
