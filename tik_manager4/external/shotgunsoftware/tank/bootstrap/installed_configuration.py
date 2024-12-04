# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from .errors import TankBootstrapError
from .configuration import Configuration
from .. import LogManager

log = LogManager.get_logger(__name__)


class InstalledConfiguration(Configuration):
    """
    Represents a Toolkit pipeline configuration that is installed at a specific location via the
    ``mac_path``, ``linux_path`` and ``windows_path`` fields that has been setup with the setup project
    command of the pre-zero config project creation wizard in PTR desktop app.
    """

    def __init__(self, path, descriptor):
        """
        :param str path: ShotgunPath object describing the path to this configuration
        :param descriptor: ConfigDescriptor for the associated config
        """
        super(InstalledConfiguration, self).__init__(path, descriptor)

    def __str__(self):
        """
        User friendly representation of the configuration.
        """
        return "Installed Configuration at %s" % (self._path.current_os,)

    def __repr__(self):
        """
        Low level representation of the configuration.
        """
        return "<%s>" % str(self)

    def status(self):
        """
        Installed configurations are always up-to-date.

        :returns: LOCAL_CFG_UP_TO_DATE
        """
        log.debug("Checking that centralized config has got all the required files.")
        # check that the path we have been given actually points at
        # a centralized configuration.
        config_path = self._path.current_os
        pipe_cfg_path = os.path.join(
            config_path, "config", "core", "pipeline_configuration.yml"
        )
        if not os.path.exists(pipe_cfg_path):

            log.warning(
                "Your centralized pipeline configuration is missing the file %s. "
                "Pipeline configurations using the fields windows_path, mac_path "
                "or linux_path need to be created via the Toolkit "
                "project setup process." % pipe_cfg_path
            )

            log.warning(
                "Note: If you want to bootstrap toolkit directly from a "
                "configuration that is stored locally, use the "
                "PipelineConfiguration.descriptor field together with a path descriptor."
            )

            raise TankBootstrapError(
                "Cannot find required system file 'config/core/pipeline_configuration.yml' "
                "in configuration %s." % config_path
            )

        log.debug(
            "Checking status of %s: Installed configs are always up to date:" % self
        )

        return self.LOCAL_CFG_UP_TO_DATE

    def update_configuration(self):
        """
        No need to update anything, as this configuration type is always up-to-date.
        """
        pass

    @property
    def requires_dynamic_bundle_caching(self):
        """
        If True, indicates that pipeline configuration relies on dynamic caching
        of bundles to operate. If False, the configuration has its own bundle
        cache.
        """
        return False
