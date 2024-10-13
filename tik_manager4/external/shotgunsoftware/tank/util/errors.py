# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Utilities related errors.
"""

from ..errors import TankError


class ShotgunAttachmentDownloadError(TankError):
    """
    Raised when a Shotgun attachment could not be downloaded
    """


class UnresolvableCoreConfigurationError(TankError):
    """
    Raises when Toolkit is not able to resolve the path
    """

    def __init__(self, full_path_to_file):
        """
        :param str full_path_to_file: Path to the folder where shotgun.yml was expected.
        """
        TankError.__init__(
            self,
            "Cannot resolve the core configuration from the location of the Sgtk Code! "
            "This can happen if you try to move or symlink the Sgtk API. The "
            "Sgtk API is currently picked up from %s which is an "
            "invalid location." % full_path_to_file,
        )


class EnvironmentVariableFileLookupError(TankError):
    """
    Raised when an environment variable specifying a location points to configuration
    file that doesn't exist.
    """

    def __init__(self, var_name, path):
        """
        :param str var_name: Name of the environment variable used.
        :param str path: Path to the configuration file that doesn't exist.
        """
        TankError.__init__(
            self,
            "The environment variable '%s' refers to a configuration file on disk at '%s' that doesn't exist."
            % (var_name, path),
        )


class ShotgunPublishError(TankError):
    """
    Raised when Toolkit is not able to register a published file in Shotgun.

    The original message for the reported error is available in the 'error_message' property.

    If a published file entity was created before the error happened, it will be
    available in the 'entity' property.
    """

    def __init__(self, error_message, entity=None):
        """
        :param str error_message: An error message, typically coming from a caught exception.
        :param dict entity: The Shotgun entity which was created, if any.
        """
        self.error_message = error_message
        self.entity = entity
        extra_message = "."
        if self.entity:
            # Mention the created entity in the message by appending something like:
            # , although TankPublishedFile dummy_path.txt (id: 2) was created.
            extra_message = ", although %s %s (id: %d) was created." % (
                self.entity["type"],
                self.entity["code"],
                self.entity["id"],
            )
        TankError.__init__(
            self,
            "Unable to complete publishing because of the following error: %s%s"
            % (self.error_message, extra_message),
        )


class PublishResolveError(TankError):
    """
    Base class for all errors relating to resolution of paths from publishes.
    """

    pass


class PublishPathNotDefinedError(PublishResolveError):
    """
    Exception raised when a publish does not have a path
    defined for the current operating system platform. It
    may or may not have publish paths defined on other
    platforms.
    """

    pass


class PublishPathNotSupported(PublishResolveError):
    """
    Exception raised when a publish has a path defined but it is using a path
    definition that cannot be resolved into a local path. This includes for
    example unsupported url schemes.
    """

    pass
