# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from __future__ import with_statement

import os

from .descriptor_config import ConfigDescriptor
from .. import pipelineconfig_utils
from .. import LogManager
from ..util import ShotgunPath
from . import constants
from .errors import TankMissingManifestError

from ..errors import (
    TankNotPipelineConfigurationError,
    TankFileDoesNotExistError,
    TankInvalidCoreLocationError,
)

log = LogManager.get_logger(__name__)


class InstalledConfigDescriptor(ConfigDescriptor):
    """
    Descriptor that describes an installed Toolkit Configuration. An installed configuration
    is what we otherwise refer to as a centralized pipeline configuration, which is a pipeline
    configuration is that installed in a folder on the network, which contains a copy of the
    environment files, a copy of core and all the bundles required by that pipeline configuration.
    It supports localized as well as shared core and as such, the interpreter files can be found
    inside the configuration folder or alongside the shared core.
    """

    def __init__(
        self, sg_connection, io_descriptor, bundle_cache_root_override, fallback_roots
    ):
        """
        .. note:: Use the factory method :meth:`create_descriptor` when
                  creating new descriptor objects.

        :param sg_connection: Connection to the current site.
        :param io_descriptor: Associated IO descriptor.
        :param bundle_cache_root_override: Override for root path to where
            downloaded apps are cached.
        :param fallback_roots: List of immutable fallback cache locations where
            apps will be searched for.
        """
        super(InstalledConfigDescriptor, self).__init__(
            sg_connection, io_descriptor, bundle_cache_root_override, fallback_roots
        )
        self._io_descriptor.set_is_copiable(False)

    @property
    def python_interpreter(self):
        """
        Retrieves the Python interpreter for the current platform from the interpreter files at
        ``config/core/interpreter_Linux.cfg``, ``config/core/interpreter_Darwin.cfg`` or
        ``config/core/interpreter_Windows.cfg``.

        .. note:: If the pipeline configuration uses a shared core, the ``core_<os>.cfg`` files will be
            followed to get to the interpreter files.

        :raises TankFileDoesNotExistError: Raised if the ``core_<os>.cfg`` file is missing for the
            pipeline configuration.
        :raises TankInvalidCoreLocationError: Raised if the core location specified in
            ``core_<os>.cfg`` does not exist.
        :returns: Path value stored in the interpreter file.
        """
        pipeline_config_path = self._get_pipeline_config_path()

        # Config is localized, we're supposed to find an interpreter file in it.
        if pipelineconfig_utils.is_localized(pipeline_config_path):
            return self._find_interpreter_location(
                os.path.join(pipeline_config_path, "config")
            )
        else:
            studio_path = self._get_core_path_for_config(pipeline_config_path)
            return self._find_interpreter_location(os.path.join(studio_path, "config"))

    @property
    def associated_core_descriptor(self):
        """
        The descriptor dict or url required for this core.

        .. note:: If the pipeline configuration uses a shared core, the ``core_<os>.cfg`` files will
            be followed and refer the shared core location.

        :returns: Core descriptor dict.
        """
        pipeline_config_path = self._get_pipeline_config_path()
        return {
            "type": "path",
            "path": os.path.join(
                self._get_core_path_for_config(pipeline_config_path), "install", "core"
            ),
        }

    def _get_manifest(self):
        """
        Returns the info.yml metadata associated with this descriptor.

        :returns: dictionary with the contents of info.yml
        """
        try:
            manifest = self._io_descriptor.get_manifest(
                os.path.join("config", constants.BUNDLE_METADATA_FILE)
            )
            # We need to tolerate empty manifests since these exists currently.
            return manifest or {}
        except TankMissingManifestError:
            return {}

    def get_config_folder(self):
        r"""
        Returns the path to the ``config`` folder inside the pipeline configuration.

        For example, for a configuration at ``\\server\mount\shotgun\project\pipeline``,
        the ``config`` folder would be at
        ``\\server\mount\shotgun\project\pipeline\config``.

        :returns: Path to the ``config`` folder.
        """
        return os.path.join(self._io_descriptor.get_path(), "config")

    def _get_pipeline_config_path(self):
        path = self.get_path()

        if not self.exists_local():
            raise TankNotPipelineConfigurationError(
                "The folder at '%s' does not contain a pipeline configuration." % path
            )

        return path

    def _get_core_path_for_config(self, pipeline_config_path):
        """
        Returns the core api install location associated with the given pipeline configuration.
        In the case of a localized PC, it just returns the given path.
        Otherwise, it resolves the location via the core_xxxx.cfg files.

        :param str pipeline_config_path: path to a pipeline configuration

        :returns: Path to the studio location root or pipeline configuration root or None if not resolved
        :rtype: str

        :raises TankFileDoesNotExistError: Raised if the core_xxxx.cfg file is missing for the
            pipeline configuration.
        :raises TankInvalidCoreLocationError: Raised if the core location specified in core_xxxx.cfg
            does not exist.
        """
        if pipelineconfig_utils.is_localized(pipeline_config_path):
            # first, try to locate an install local to this pipeline configuration.
            # this would find any localized APIs.
            install_path = pipeline_config_path

        else:
            # this pipeline config is associated with a shared API (studio install)
            # follow the links defined in the configuration to establish which
            # setup it has been associated with.
            studio_linkback_file = self._get_current_platform_core_location_file_name(
                pipeline_config_path
            )

            if not os.path.exists(studio_linkback_file):
                raise TankFileDoesNotExistError(
                    "Configuration at '%s' without a localized core is missing a core location file at '%s'"
                    % (pipeline_config_path, studio_linkback_file)
                )

            # this file will contain the path to the API which is meant to be used with this PC.
            install_path = None
            with open(studio_linkback_file, "rt") as fh:
                # remove any whitespace, keep text
                data = fh.read().strip()

            # expand any env vars that are used in the files. For example, you could have
            # an env variable $STUDIO_TANK_PATH=/sgtk/software/shotgun/studio and your
            # linkback file may just contain "$STUDIO_TANK_PATH" instead of an explicit path.
            data = os.path.expanduser(os.path.expandvars(data))
            if data not in ["None", "undefined"] and os.path.exists(data):
                install_path = data
            else:
                raise TankInvalidCoreLocationError(
                    "Cannot find core location '%s' defined in "
                    "config file '%s'." % (data, studio_linkback_file)
                )

        return install_path

    def _get_current_platform_core_location_file_name(self, install_root):
        """
        Retrieves the path to the core location file for a given install root.

        :param str install_root: This can be the root to a studio install for a core
            or a pipeline configuration root.

        :returns: Path for the current platform's core location file.
        :rtype: str
        """
        return ShotgunPath.get_file_name_from_template(
            os.path.join(install_root, "install", "core", "core_%s.cfg")
        )
