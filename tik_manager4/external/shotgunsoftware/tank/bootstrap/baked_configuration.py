# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from .configuration import Configuration
from .configuration_writer import ConfigurationWriter

from .. import LogManager
from .. import constants

from ..util import ShotgunPath
from ..util.pickle import store_env_var_pickled
from ..errors import TankFileDoesNotExistError
from .. import pipelineconfig_utils

log = LogManager.get_logger(__name__)


class BakedConfiguration(Configuration):
    """
    Represents a configuration that has been baked out at build time,
    containing incomplete state data - at bake time we don't yet know
    what project id, what site, configuration id etc. will be required.
    """

    def __init__(
        self,
        path,
        sg,
        project_id,
        plugin_id,
        pipeline_config_id,
        bundle_cache_fallback_paths,
        descriptor,
    ):
        """
        Constructor.

        :param path: ShotgunPath object describing the path to this configuration
        :param sg: Shotgun API instance
        :param project_id: Project id for the shotgun project associated with the
                           configuration. For a site-level configuration, this
                           can be set to None.
        :param plugin_id: Plugin id string to identify the scope for a particular plugin
                          or integration. For more information,
                          see :meth:`~sgtk.bootstrap.ToolkitManager.plugin_id`. For
                          non-plugin based toolkit projects, this value is None.
        :param pipeline_config_id: Pipeline Configuration id for the shotgun
                                   pipeline config id associated. If a config does
                                   not have an associated entity in Shotgun, this
                                   should be set to None.
        :param bundle_cache_fallback_paths: List of additional paths where apps are cached.
        :param descriptor: ConfigDescriptor for the associated config
        """
        super(BakedConfiguration, self).__init__(path, descriptor)
        self._path = path
        self._sg_connection = sg

        self._project_id = project_id
        self._plugin_id = plugin_id
        self._pipeline_config_id = pipeline_config_id
        self._bundle_cache_fallback_paths = bundle_cache_fallback_paths

    def __str__(self):
        """
        User friendly representation of the config
        """
        return "Pre-baked config '%s'" % self._path

    def __repr__(self):
        """
        Low level representation of the config.
        """
        return "<Pre-baked config '%s'>" % self._path

    def status(self):
        """
        Compares the actual configuration installed on disk against the
        associated configuration described by the descriptor passed in via
        the class constructor.

        :returns: LOCAL_CFG_UP_TO_DATE, LOCAL_CFG_MISSING,
                  LOCAL_CFG_DIFFERENT, or LOCAL_CFG_INVALID
        """
        return self.LOCAL_CFG_UP_TO_DATE

    def update_configuration(self):
        """
        Ensure that the configuration is up to date with the one
        given by the associated descriptor.

        In the case of a baked configuration everything has been
        baked into a static setup at build time so this method
        does not do anything.
        """
        pass

    def get_tk_instance(self, sg_user):
        """
        Returns a tk instance for this configuration.

        :param sg_user: Authenticated Shotgun user to associate
                        the tk instance with.
        """

        # Heads up that the base implementation is not called: we totally
        # override it.

        # set up the environment to pass on to the tk instance
        pipeline_config = {
            "project_id": self._project_id,
            "pipeline_config_id": self._pipeline_config_id,
            "bundle_cache_paths": self._bundle_cache_fallback_paths,
        }

        log.debug("Setting External config data: %s" % pipeline_config)
        store_env_var_pickled(
            constants.ENV_VAR_EXTERNAL_PIPELINE_CONFIG_DATA, pipeline_config
        )

        path = self._path.current_os
        try:
            python_core_path = pipelineconfig_utils.get_core_python_path_for_config(
                path
            )
        except TankFileDoesNotExistError:
            # For baked config we allow a globally installed tk-core to be used
            python_core_path = self._get_current_core_python_path()
            log.debug(
                "Couldn't retrieve a core path from the config, keeping current one: %s"
                % (python_core_path)
            )

        self._swap_core_if_needed(python_core_path)

        # Perform a local import here to make sure we are getting
        # the newly swapped in core code, if it was swapped
        from .. import api

        # Baked config are typically not attached to any Shotgun site, or project
        # so we can simply keep using the current user, which holds Shotgun
        # connection informations.
        api.set_authenticated_user(sg_user)

        return self._tank_from_path(path), sg_user

    @classmethod
    def bake_config_scaffold(cls, path, sg_connection, plugin_id, config_descriptor):
        """
        Helper method that can be used to generate a baked scaffold in a given path.

        :param path: Path to generate scaffold in.
        :param sg_connection: Shotgun API instance
        :param plugin_id: Plugin id string to identify the scope for a particular plugin
                          or integration. For more information,
                          see :meth:`~sgtk.bootstrap.ToolkitManager.plugin_id`. For
                          non-plugin based toolkit projects, this value is None.
        :param config_descriptor: Descriptor object describing the configuration.
        """
        # Write out a baked configuration - this is just like one of the
        # configurations that are written out at runtime for cached configs,
        # but with the difference that this will be bundled with an installation
        # and therefore needs to be completely location agnostic.
        config_writer = ConfigurationWriter(
            ShotgunPath.from_current_os_path(path), sg_connection
        )

        config_writer.ensure_project_scaffold()
        config_descriptor.copy(os.path.join(path, "config"))
        config_writer.install_core(config_descriptor.resolve_core_descriptor())

        # write the pipeline_config.yml file but do not include the
        # source_descriptor - setting this to None indicates
        # that this should be looked up at runtime.
        config_writer.write_pipeline_config_file(
            pipeline_config_id=None,
            project_id=None,
            plugin_id=plugin_id,
            bundle_cache_fallback_paths=[],
            source_descriptor=None,
        )

        # Same thing here as above for the install_location file. We don't really
        # need the tank command and interpreter_*.cfg files for the config itself,
        # but other logic in tk-core relies on them existing.
        config_writer.create_tank_command()

    @property
    def requires_dynamic_bundle_caching(self):
        """
        If True, indicates that pipeline configuration relies on dynamic caching
        of bundles to operate. If False, the configuration has its own bundle
        cache.
        """
        # Baked configurations always have a local bundle install folder.
        return False
