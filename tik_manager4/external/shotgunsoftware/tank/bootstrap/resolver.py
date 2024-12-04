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
Resolver module. This module provides a way to resolve a pipeline configuration
on disk.
"""

import sys
import os
import fnmatch
import pprint

from ..descriptor import (
    Descriptor,
    create_descriptor,
    descriptor_uri_to_dict,
    is_descriptor_version_missing,
)
from .errors import TankBootstrapError, TankBootstrapInvalidPipelineConfigurationError
from .baked_configuration import BakedConfiguration
from .cached_configuration import CachedConfiguration
from .installed_configuration import InstalledConfiguration
from ..descriptor.descriptor_installed_config import InstalledConfigDescriptor
from ..util import filesystem
from ..util import ShotgunPath
from ..util import LocalFileStorageManager
from .. import LogManager
from . import constants

log = LogManager.get_logger(__name__)


class ConfigurationResolver(object):
    """
    A class that contains the business logic for returning a configuration
    object given a set of parameters.
    """

    _PIPELINE_CONFIG_FIELDS = [
        "code",
        "project",
        "users",
        "plugin_ids",
        "sg_plugin_ids",
        "windows_path",
        "linux_path",
        "mac_path",
        "sg_descriptor",
        "descriptor",
        "uploaded_config",
        "sg_uploaded_config",
    ]

    def __init__(self, plugin_id, project_id=None, bundle_cache_fallback_paths=None):
        """
        Constructor

        :param plugin_id: The plugin id of the system that is being bootstrapped.
        :param project_id: Project id to create a config object for, ``None`` for the site config.
        :param bundle_cache_fallback_paths: Optional list of additional paths where apps are cached.
        """
        self._project_id = project_id
        self._proj_entity_dict = (
            {"type": "Project", "id": self._project_id} if self._project_id else None
        )
        self._plugin_id = plugin_id
        self._bundle_cache_fallback_paths = bundle_cache_fallback_paths or []

    def __repr__(self):
        return "<Resolver: proj id %s, plugin id %s>" % (
            self._project_id,
            self._plugin_id,
        )

    def resolve_configuration(self, config_descriptor, sg_connection):
        """
        Return a configuration object given a config descriptor

        :param config_descriptor: descriptor dict or string
        :param sg_connection: Shotgun API instance
        :return: :class:`Configuration` instance
        """
        log.debug(
            "%s resolving configuration for descriptor %s" % (self, config_descriptor)
        )

        if config_descriptor is None:
            raise TankBootstrapError(
                "No config descriptor specified - Cannot create a configuration object."
            )

        # convert to dictionary form
        if isinstance(config_descriptor, str):
            # convert to dict so we can introspect
            config_descriptor = descriptor_uri_to_dict(config_descriptor)

        if config_descriptor["type"] == constants.BAKED_DESCRIPTOR_TYPE:
            # special case -- this is a full configuration scaffold that
            # has been pre-baked and can be used directly at runtime
            # without having to do lots of copying into temp space.
            baked_config_root = None
            log.debug("Searching for baked config %s" % config_descriptor)
            for root_path in self._bundle_cache_fallback_paths:
                baked_config_path = os.path.join(
                    root_path,
                    constants.BAKED_DESCRIPTOR_FOLDER_NAME,
                    config_descriptor["name"],
                    config_descriptor["version"],
                )
                if os.path.exists(baked_config_path):
                    log.debug("Located baked config in %s" % baked_config_path)
                    # only handle current os platform
                    baked_config_root = ShotgunPath.from_current_os_path(
                        baked_config_path
                    )
                    break

            if baked_config_root is None:
                raise TankBootstrapError("Cannot locate %s!" % config_descriptor)

            cfg_descriptor = create_descriptor(
                sg_connection,
                Descriptor.CONFIG,
                dict(path=baked_config_path, type="path"),
                fallback_roots=self._bundle_cache_fallback_paths,
                resolve_latest=False,
            )

            # create an object to represent our configuration install
            config_path = ShotgunPath.from_current_os_path(cfg_descriptor.get_path())
            return BakedConfiguration(
                config_path,
                sg_connection,
                self._project_id,
                self._plugin_id,
                None,
                self._bundle_cache_fallback_paths,
                cfg_descriptor,
            )
        else:
            # now probe for a version token in the given descriptor.
            # if that exists, a fixed version workflow will be used where
            # that exact version of the config is used.
            #
            # if a version token is omitted, we request that the latest version
            # should be resolved.
            if is_descriptor_version_missing(config_descriptor):
                log.debug(
                    "Base configuration descriptor does not have a "
                    "version token defined. Will attempt to determine "
                    "the latest version available."
                )
                resolve_latest = True
            else:
                log.debug(
                    "Base configuration has a version token defined. "
                    "Will use this fixed version for the bootstrap."
                )
                resolve_latest = False

            cfg_descriptor = create_descriptor(
                sg_connection,
                Descriptor.CONFIG,
                config_descriptor,
                fallback_roots=self._bundle_cache_fallback_paths,
                resolve_latest=resolve_latest,
            )

            return self._create_configuration_from_descriptor(
                cfg_descriptor, sg_connection, pc_id=None
            )

    def resolve_not_found_sg_configuration(self, config_descriptor, sg_connection):
        """
        Creates a configuration object given a config fallback descriptor this
        means not pipeline config record was found in shotgrid, so
        we request that the latest version should be resolved based on
        this associated descriptor object.

        :param config_descriptor: Fallback descriptor dict or string
        :param sg_connection: Shotgun API instance
        :return: :class:`Configuration` instance
        """

        if config_descriptor is None:
            raise TankBootstrapError(
                "No config descriptor specified - Cannot create a configuration object."
            )

        # convert to dictionary form
        if isinstance(config_descriptor, str):
            # convert to dict so we can introspect
            config_descriptor = descriptor_uri_to_dict(config_descriptor)
        # This is a special case covered in resolve_configuration()
        if config_descriptor["type"] == constants.BAKED_DESCRIPTOR_TYPE:
            return self.resolve_configuration(config_descriptor, sg_connection)

        # Validate if descriptor version token is omitted
        resolve_latest = is_descriptor_version_missing(config_descriptor)
        if (
                sys.version_info[0] < 3
                and self._plugin_id == "basic.desktop"
                and resolve_latest
        ):
            # This will avoid auto update your tk-config-basic configuration to the
            # latest available version when running Python 2.
            # This cover the following case:
            #
            # * PTR desktop app is launched using Python 2 by setting 'SHOTGUN_PYTHON_VERSION'
            #   environment variable to '2'and it will startup the tk-desktop engine for
            #   the Site configuration.
            #
            # In this case this will initialize the tk-desktop for the 'Site' environment and
            # resolve a configuration object using a descriptor pointing to the maximum config
            # version supporting Python 2 which is maintained in the variable
            # 'MAX_CONFIG_BASIC_PYTHON2_SUPPORTED' in the bootstrap constants.
            log.info(
                "Using Python version '%s'" % ".".join(str(i) for i in sys.version_info[0:3])
            )
            log.debug(
                "Base configuration descriptor does not have a "
                "version token defined."
            )

            # Disable resolve latest
            resolve_latest = False
            # Make sure the configuration version points to the latest
            # supporting Python2
            config_descriptor["version"] = constants.MAX_CONFIG_BASIC_PYTHON2_SUPPORTED
            log.debug(
                "%s Resolving configuration for latest version supporting Python 2 descriptor %s" % (self, config_descriptor)
            )
            # create config descriptor
            cfg_descriptor = create_descriptor(
                sg_connection,
                Descriptor.CONFIG,
                config_descriptor,
                fallback_roots=self._bundle_cache_fallback_paths,
                resolve_latest=resolve_latest,
            )

        else:
            # Resolve config normally
            return self.resolve_configuration(config_descriptor, sg_connection)

        return self._create_configuration_from_descriptor(
            cfg_descriptor, sg_connection, pc_id=None
        )

    def _create_configuration_from_descriptor(
        self, cfg_descriptor, sg_connection, pc_id
    ):
        """
        Creates a Configuration instance based on its associated descriptor object.

        :param cfg_descriptor: ConfigDescriptor for which we want to create a Configuration object.
        :param sg_connection: Connection to Shotgun.
        :param pc_id: Id of the pipeline configuration in Shotgun. Can be ``None``.
        """

        log.debug("Creating Configuration instance from %r." % cfg_descriptor)

        # If we're dealing with an installed configuration descriptor, we need to make sure
        # it actually exists on disk.
        if isinstance(cfg_descriptor, InstalledConfigDescriptor):
            if not cfg_descriptor.exists_local():
                raise TankBootstrapError(
                    "Installed pipeline configuration '%s' does not exist on disk!"
                    % cfg_descriptor.get_uri()
                )

            config_path = ShotgunPath.from_current_os_path(cfg_descriptor.get_path())
            # The configuration path here points to the actual pipeline configuration that contains
            # config, cache and install folders.
            return InstalledConfiguration(config_path, cfg_descriptor)

        else:
            # first get the cache root
            cache_root = LocalFileStorageManager.get_configuration_root(
                sg_connection.base_url,
                self._project_id,
                self._plugin_id,
                pc_id,
                LocalFileStorageManager.CACHE,
            )

            # resolve the config location both based on plugin id and current engine.
            #
            # Example: ~/Library/Caches/Shotgun/mysitename/site.review.rv/cfg
            #
            config_cache_root = os.path.join(cache_root, "cfg")
            filesystem.ensure_folder_exists(config_cache_root)

            log.debug("Configuration root resolved to %s." % config_cache_root)

            # populate current platform, leave rest blank.
            # this resolver only supports local, on-the-fly
            # configurations
            config_root = ShotgunPath.from_current_os_path(config_cache_root)

            # create an object to represent our configuration install
            return CachedConfiguration(
                config_root,
                sg_connection,
                cfg_descriptor,
                self._project_id,
                self._plugin_id,
                pc_id,
                self._bundle_cache_fallback_paths,
            )

    def _get_pipeline_configurations_for_project(
        self, pipeline_config_name, current_login, sg_connection
    ):
        """
        Retrieves pipeline configurations from Shotgun that are compatible with the given project.

        :param str pipeline_config_name: Name of the pipeline configuration requested for. If ``None``,
            all pipeline configurations from the project will be matched.
        :param str current_login: Only retains non-primary configs from the specified user.
        :param ``shotgun_api3.Shotgun`` sg_connection: Connection to the Shotgun site.

        :returns: A list of pipeline configuration entity dictionaries with an
                  extra key 'config_descriptor' added representing a resolved descriptor
                  instance pointing at the associated configuration to be used for this
                  pipeline configuration. Please note that this method returns all
                  pipeline configs matching the given project, meaning that sometimes
                  the 'config_descriptor' key may be ``None``, for example in the case where
                  a pipeline configuration is defined for the project for Windows and you
                  are currently running on a mac.
        :rtype: list
        """
        # get the pipeline configs for the current project which are
        # either the primary or is associated with the currently logged in user.
        # also get the pipeline configs for the site level (project=None)
        log.debug("Requesting pipeline configurations from Flow Production Tracking...")

        if pipeline_config_name is None:
            # If nothing was specified, we need to pick pipeline configurations...
            ownership_filter = {
                "filter_operator": "any",
                "filters": [
                    [
                        "users.HumanUser.login",
                        "is",
                        current_login,
                    ],  # ... that are owned by the user OR
                    ["users", "is", None],  # ... that are shared.
                ],
            }
        elif pipeline_config_name == constants.PRIMARY_PIPELINE_CONFIG_NAME:
            # Only retrieve primary.
            # This makes sense if you don't want sandboxes and specifically want the Primary.
            ownership_filter = ["code", "is", constants.PRIMARY_PIPELINE_CONFIG_NAME]
        else:
            # If someone requested a pipeline by name that wasn't primary, it means we need only sandboxes,
            # in which case...
            ownership_filter = {
                "filter_operator": "all",
                "filters": [
                    [
                        "code",
                        "is",
                        pipeline_config_name,
                    ],  # .. we only want pipeines with a given name AND
                    {
                        "filter_operator": "any",
                        "filters": [
                            [
                                "users.HumanUser.login",
                                "is",
                                current_login,
                            ],  # ... who are assigned to the user OR
                            ["users", "is", None],  # ... that are shared.
                        ],
                    },
                ],
            }

        filters = [
            {
                "filter_operator": "any",
                "filters": [
                    ["project", "is", self._proj_entity_dict],
                    ["project", "is", None],
                ],
            },
            ownership_filter,
        ]

        log.debug("Retrieving the pipeline configuration list:")
        log.debug(pprint.pformat(filters))

        pipeline_configs = sg_connection.find(
            "PipelineConfiguration",
            filters,
            self._PIPELINE_CONFIG_FIELDS,
            order=[{"field_name": "id", "direction": "asc"}],
        )

        log.debug(
            "The following pipeline configurations were found: %s"
            % pprint.pformat(pipeline_configs)
        )

        # loop over all pipeline configs
        for pipeline_config in pipeline_configs:

            # see if the pipeline configuration we are looking at is relevant. Either of:
            # - Be a match against the resolver's associated plugin id
            # - Be a centralized config associated with the resolver's associated project

            if self._matches_current_plugin_id(
                pipeline_config
            ) or self._is_centralized_pc_for_current_project(pipeline_config):

                # extract the location information and place in special 'config_descriptor'
                # field. Note that this may be None if for example the pipeline configuration
                # is defined for another operating system.
                try:
                    pipeline_config[
                        "config_descriptor"
                    ] = self._create_config_descriptor(sg_connection, pipeline_config)
                    yield pipeline_config

                except TankBootstrapInvalidPipelineConfigurationError as e:
                    log.warning(
                        "Pipeline configuration %s does not define a valid "
                        "access location. Details: %s" % (pipeline_config, e)
                    )

    def _create_config_descriptor(self, sg_connection, shotgun_pc_data):
        """
        Creates a configuration descriptor for a given pipeline configuration entry.

        :param sg_connection: Connection to Shotgun.
        :param dict shotgun_pc_data: Pipeline configuration dictionary with keys ``descriptor``,
            ``sg_descriptor`` and ``*_path`.

        :returns: A :class:`sgtk.descriptor.ConfigDescriptorBase` instance or ``None`` if the
            pipeline configuration is valid but defines a configuration which cannot be
            reached from the current runtime environment. The typical example when this
            happens is if a pipeline configuration defines a path for some operating
            systems only.

        :raises TankBootstrapInvalidPipelineConfigurationError: If the given pipeline configuration
            does not define a configuration to use.
        """
        # As in resolve_shotgun_configuration, the order of precedence
        # is as follows:
        #
        # 1. windows/linux/mac path
        # 2. descriptor
        # 3. sg_descriptor
        # 4. uploaded_config
        # 5. sg_uploaded_config

        path = ShotgunPath.from_shotgun_dict(shotgun_pc_data)
        sg_descriptor_uri = shotgun_pc_data.get("descriptor") or shotgun_pc_data.get(
            "sg_descriptor"
        )
        sg_uploaded_config = shotgun_pc_data.get(
            "uploaded_config"
        ) or shotgun_pc_data.get("sg_uploaded_config")

        # centralized configs are defined by having their plugin_ids field set to None
        # centralized configs only support the path fields
        plugin_ids = shotgun_pc_data.get("plugin_ids") or shotgun_pc_data.get(
            "sg_plugin_ids"
        )
        is_centralized_config = plugin_ids is None

        cfg_descriptor = None

        if path:
            if sg_descriptor_uri or sg_uploaded_config:
                log.debug(
                    "Multiple configuration fields defined for pipeline configuration %s. "
                    "Using path based field.",
                    shotgun_pc_data["id"],
                )

            # Make sure that the config has a path for the current OS.
            if path.current_os is None:
                log.debug(
                    "Config isn't setup for %s: %s", sys.platform, shotgun_pc_data
                )
                cfg_descriptor = None
            else:
                # Create an installed descriptor
                descriptor_dict = path.as_shotgun_dict()
                descriptor_dict["type"] = "path"
                cfg_descriptor = create_descriptor(
                    sg_connection,
                    Descriptor.INSTALLED_CONFIG,
                    descriptor_dict,
                    fallback_roots=self._bundle_cache_fallback_paths,
                )

        elif sg_descriptor_uri and not is_centralized_config:

            if sg_uploaded_config:
                log.debug(
                    "Multiple configuration fields defined for pipeline configuration %s. "
                    "Using descriptor based field.",
                    shotgun_pc_data["id"],
                )

            if shotgun_pc_data.get("sg_descriptor"):
                log.debug(
                    "Both sg_descriptor and descriptor fields are set on pipeline configuration "
                    "%s. Using descriptor field.",
                    shotgun_pc_data["id"],
                )

            cfg_descriptor = create_descriptor(
                sg_connection,
                Descriptor.CONFIG,
                sg_descriptor_uri,
                fallback_roots=self._bundle_cache_fallback_paths,
                resolve_latest=is_descriptor_version_missing(sg_descriptor_uri),
            )

        elif sg_uploaded_config and not is_centralized_config:

            if shotgun_pc_data.get("uploaded_config") and shotgun_pc_data.get(
                "sg_uploaded_config"
            ):
                log.debug(
                    "Both sg_uploaded_config and uploaded_config fields are set on pipeline configuration "
                    "%s. Using uploaded_config field.",
                    shotgun_pc_data["id"],
                )

            if sg_uploaded_config == shotgun_pc_data.get("uploaded_config"):
                uploaded_config_field_name = "uploaded_config"
            else:
                uploaded_config_field_name = "sg_uploaded_config"

            # make sure that it is an uploaded attachment and not a url or local file link
            if shotgun_pc_data[uploaded_config_field_name].get("link_type") != "upload":
                raise TankBootstrapInvalidPipelineConfigurationError(
                    "Cannot resolve uploaded config for pipeline configuration %s: "
                    "Only uploaded attachments are currently supported"
                    % shotgun_pc_data["id"]
                )

            #
            # NOTE! The format where we can pass id/version/entity_type/field to the shotgun
            #       descriptor was added as part of core 18.120 - older cores will not recognize it
            #       this means that the config we are bootstrapping into here needs to use a core
            #       more recent than 120 in order to understand this form.
            #
            sg_descriptor_uri = dict(
                type="shotgun",
                entity_type="PipelineConfiguration",
                id=shotgun_pc_data["id"],
                version=sg_uploaded_config[
                    "id"
                ],  # Attachment id changes for each upload, so
                # this is a good way to detect changes in the zip file.
                field=uploaded_config_field_name,
            )

            cfg_descriptor = create_descriptor(
                sg_connection,
                Descriptor.CONFIG,
                sg_descriptor_uri,
                fallback_roots=self._bundle_cache_fallback_paths,
            )

        else:

            # If we have neither a uri, nor a path, raise exception
            # to indicate that config is not valid.
            if plugin_ids is None and (sg_descriptor_uri or sg_uploaded_config):
                # there is an uploaded config or descriptor specified but
                # plugin_ids has not been set. This is a common thing
                # to forget so it's important to provide a clear error message
                msg = (
                    "Pipeline Configuration %s does not have a "
                    "plugin_ids pattern specified." % shotgun_pc_data["id"]
                )

            elif is_centralized_config:
                # plugin_ids is None and no descriptor/uploaded config field set.
                # assume this is a centralized config
                msg = (
                    "Centralized Pipeline Configuration %s does not have "
                    "a mac/windows/linux_path field specified." % shotgun_pc_data["id"]
                )

            else:
                # plugin ids is set but nothing else.
                msg = (
                    "Pipeline Configuration %s does not have "
                    "a descriptor uri or uploaded config specified."
                    % shotgun_pc_data["id"]
                )

            raise TankBootstrapInvalidPipelineConfigurationError(msg)

        if cfg_descriptor is None:
            log.debug(
                "Unable to resolve descriptor for config: \n%s",
                pprint.pformat(shotgun_pc_data),
            )
        else:
            log.debug(
                "Config descriptor resolved. \nConfig: %s \nDescriptor: %r",
                pprint.pformat(shotgun_pc_data),
                cfg_descriptor,
            )

        return cfg_descriptor

    def _pick_primary_pipeline_config(self, configs, level_name):
        """
        Picks a primary pipeline configuration and logs warnings if where are any extra ones.

        If there is a Toolkit centralized pipeline configuration, it is picked over any plugin-id based
        pipeline configurations. If there are multiple Toolkit centralized pipeline configurations,
        the one with the lowest id is picked.

        :param list configs: Pipeline configurations entities sorted by id from lowest to highest.
        :param str level_name: Name of the scope for the pipeline configurations.

        :returns: The first pipeline configuration from ``configs`` or ``None`` if it was empty.
        """

        # Sorts all pipeline configurations, putting all centralized pipeline configurations in the
        # front and then all the plugin based at the back. In each group, pipelines are sorted
        # by id.
        def make_pc_key(pc):
            if pc.get("plugin_ids") or pc.get("sg_plugin_ids"):
                return (1, pc["id"])
            else:
                return (0, pc["id"])

        configs = sorted(configs, key=make_pc_key)

        first, remainder = configs[0:1], configs[1:]

        if remainder:
            log.warning("Too many %s level pipeline configurations found.", level_name)
            log.warning(
                "Non-plugin id based pipeline configuration always take precedence over plugin id based"
                "pipeline configurations. Lower id pipeline configurations always take precedence over"
                "higher id pipeline configurations."
            )
            log.warning("The following pipeline configurations were skipped:")
            for pc in remainder:
                log.warning(
                    "    - Name: %s, Id: %s, Plugin Ids: %s",
                    pc["code"],
                    pc["id"],
                    pc.get("sg_plugin_ids") or pc.get("plugin_ids") or "None",
                )

        # Return the first item if available, None otherwise.
        return first[0] if first else None

    def _filter_pipeline_configurations(self, pcs):
        """
        Filters pipeline configurations that are not needed.

        Here are the rules for being kept:
           - There can only be one primary
           - If there is one site level and one project level primary,
             the project level one is returned.
           - If there are two site level or two project level primaries, the one with the lowest id is kept.
           - All sandboxes are returned.

        .. note: This code assumes that pipeline configurations are sorted by id.

        :param list pcs: List of pipeline configuration entities with keys `code` and `project`.

        :returns: A tuple containing:
            - The primary pipeline configuration, if found.
            - An array of dev sandboxes for the current project, if found.
            - The primary site level pipeline configuration, if found and theres no primary project configuration.

        :rtype: tuple(dict, list, list)
        """
        primary_project_configs = []
        user_project_configs = []
        primary_site_configs = []
        user_site_configs = []

        # Step 1: Sort each pipeline in its respective bucket.
        for pc in pcs:
            if self._is_project_pc(pc):
                if self._is_primary_pc(pc):
                    log.debug("Primary match: %s" % pc)
                    primary_project_configs.append(pc)
                else:
                    user_project_configs.append(pc)
                    log.debug("Per-user match: %s" % pc)
            else:
                #
                if self._is_primary_pc(pc):
                    primary_site_configs.append(pc)
                    log.debug("Found primary fallback match: %s" % pc)
                else:
                    user_site_configs.append(pc)
                    log.debug("Found per-user fallback match: %s" % pc)

        # Step 2: Ensure each primary category only has one item.
        project_primary = self._pick_primary_pipeline_config(
            primary_project_configs, "project"
        )
        site_primary = self._pick_primary_pipeline_config(primary_site_configs, "site")

        # Step 3: Ensure project primary override the site primary.
        if project_primary and site_primary:
            log.info(
                "'Primary' pipeline configuration '%d' for project '%d' overrides "
                "'Primary' pipeline configuration '%d' for site.",
                project_primary["id"],
                self._project_id,
                site_primary["id"],
            )
        primary = project_primary or site_primary

        return primary, user_project_configs, user_site_configs

    def find_matching_pipeline_configurations(
        self, pipeline_config_name, current_login, sg_connection
    ):
        """
        Retrieves the pipeline configurations that can be used with this project.

        See _filter_pipeline_configurations to learn more about the pipeline configurations that are considered usable.

        :param str pipeline_config_name: Name of the pipeline configuration requested for. If ``None``,
            all pipeline configurations from the project will be matched.
        :param str current_login: Only retains non-primary configs from the specified user.
        :param ``shotgun_api3.Shotgun`` sg_connection: Connection to the Shotgun site.

        :returns: The pipeline configurations that can be used with this project. The pipeline
            configurations will always be sorted such as the primary pipeline configuration, if available,
            will be first. Then the remaining pipeline configurations will be sorted by ``name`` field
            (case insensitive), then the ``project`` field and finally then ``id`` field.
        """
        pcs = self._get_pipeline_configurations_for_project(
            pipeline_config_name, current_login, sg_connection
        )

        # Filter out pipeline configurations that are not usable.
        (
            primary,
            user_sandboxes_project,
            user_sandboxes_site,
        ) = self._filter_pipeline_configurations(pcs)

        return self._sort_pipeline_configurations(
            ([primary] if primary else [])
            + user_sandboxes_project
            + user_sandboxes_site
        )

    def _sort_pipeline_configurations(self, pcs):
        """
        Sorts pipeline configuration is primary-ness, name, project and finally id.

        :param list pcs: List of pipeline configuration dictionaries with keys ``code``, ``project`` and ``id``.

        :returns: List of sorted pipeline configuration dictionaries.
        :rtype: list
        """

        def pc_key_func(pc):
            """
            Generates a key for a pipeline configuration. The key will ensure that a Primary
            pipeline configuration goes to the front of the line.

            Everything else will be sorted by name, project and finally id.
            """
            if pc["code"] == "Primary":
                primary_index = 0
            else:
                primary_index = 1

            # Dictionary comparison is not supported in Python 3.  We will
            # replicate the previous behavior by sorting on project ID, and putting
            # configurations with no project first.
            project = -1 if pc["project"] is None else pc["project"].get("id", 0)

            return (primary_index, pc["code"].lower(), project, pc["id"])

        return sorted(pcs, key=pc_key_func)

    def _is_primary_pc(self, pc):
        """
        Tests if a pipeline configuration is a sandbox.

        :param pc: Pipeline configuration entity.

        :returns: True if pipeline configuration is a primary, False otherwise.
        """
        return pc["code"] == constants.PRIMARY_PIPELINE_CONFIG_NAME

    def _is_project_pc(self, pc):
        """
        Tests if a pipeline configuration is attached to a project.

        :param pc: Pipeline configuration entity.

        :returns: True if the pipeline configuration is attached to a project, False otherwise.
        """
        return pc.get("project") is not None

    def resolve_shotgun_configuration(
        self,
        pipeline_config_identifier,
        fallback_config_descriptor,
        sg_connection,
        current_login,
    ):
        """
        Return a configuration object by requesting a pipeline configuration
        in Shotgun. If no suitable configuration is found, return a configuration
        for the given fallback config.

        :param pipeline_config_identifier: Name or id of configuration branch (e.g Primary).
                                           If None, the method will automatically attempt
                                           to resolve the right configuration based on the
                                           current user and the users field on the pipeline
                                           configuration.
        :param fallback_config_descriptor: descriptor dict or string for fallback config.
        :param sg_connection: Shotgun API instance
        :param current_login: The login of the currently logged in user.

        :return: :class:`Configuration` instance
        """
        log.debug(
            "%s resolving configuration from PTR Pipeline Configuration %s"
            % (self, pipeline_config_identifier)
        )

        pipeline_config = None

        if not isinstance(pipeline_config_identifier, int):
            log.debug("Will auto-detect which pipeline configuration to use.")

            # Get all the pipeline configurations that can be used given our project
            # restriction.
            pcs = self._get_pipeline_configurations_for_project(
                pipeline_config_identifier, current_login, sg_connection
            )

            # Filter out pipeline configurations that are not usable.
            (
                primary,
                user_project_configs,
                user_site_configs,
            ) = self._filter_pipeline_configurations(pcs)

            # Now select in order of priority. Note that the earliest pipeline encountered for sandboxes
            # is the one that will be selected.
            if user_project_configs:
                # A per-user pipeline config for the current project has top priority
                pipeline_config = user_project_configs[0]

            elif primary and self._is_project_pc(primary):
                # if there is a primary config for our current project, this takes precedence
                pipeline_config = primary

            elif user_site_configs:
                # if there is a pipeline config for our current user with project field None
                # that takes precedence
                pipeline_config = user_site_configs[0]

            elif primary and not self._is_project_pc(primary):
                # Lowest priority - A Primary pipeline configuration with project field None
                pipeline_config = primary

            else:
                # we may not have any pipeline configuration matches at all:
                pipeline_config = None
        else:
            log.debug(
                "Will use pipeline configuration id '%s'" % pipeline_config_identifier
            )

            log.debug("Requesting pipeline configuration data from Flow Production Tracking...")

            # Fetch the one and only config that matches this id.
            pipeline_config = sg_connection.find_one(
                "PipelineConfiguration",
                [["id", "is", pipeline_config_identifier]],
                self._PIPELINE_CONFIG_FIELDS,
            )

            # If it doesn't exist, we're in trouble.
            if pipeline_config is None:
                raise TankBootstrapError(
                    "Pipeline configuration with id '%d' doesn't exist for project id '%d' in Flow Production Tracking."
                    % (pipeline_config_identifier, self._proj_entity_dict["id"])
                )

            pipeline_config["config_descriptor"] = self._create_config_descriptor(
                sg_connection, pipeline_config
            )

        # now resolve the descriptor to use based on the pipeline config record
        # default to the fallback descriptor
        # If no pipeline configuration was found in Shotgun, we will use the fallback descriptor.
        if pipeline_config is None:
            log.debug("No pipeline configuration found. Using fallback descriptor")

            # We couldn't resolve anything from Shotgun, so we'll resolve the configuration using
            # an offline resolve.
            return self.resolve_not_found_sg_configuration(fallback_config_descriptor, sg_connection)

        else:
            # Something was found in Shotgun, which means we've also potentially resolved its
            # descriptor!
            log.debug(
                "The following pipeline configuration will be used: %s"
                % pprint.pformat(pipeline_config)
            )

            pc_id = pipeline_config["id"]

            # If the selected pipeline configuration has no associated configuration descriptor, we
            # can't do anything about that.
            if pipeline_config["config_descriptor"] is None:
                log.debug(
                    'No source set for %s on the Pipeline Configuration "%s" (id %d).',
                    sys.platform,
                    pipeline_config["code"],
                    pipeline_config["id"],
                )
                raise TankBootstrapError(
                    "The PTR pipeline configuration with id %s has no source location specified for "
                    "your operating system." % pipeline_config["id"]
                )
            config_descriptor = pipeline_config["config_descriptor"]

            log.debug(
                "The descriptor representing the config is %r" % config_descriptor
            )

            return self._create_configuration_from_descriptor(
                config_descriptor, sg_connection, pc_id
            )

    def _is_centralized_pc_for_current_project(self, shotgun_pc_data):
        """
        Checks if a pipeline configuration is a centralized pipeline configuration,
        for the requested project.

        :param dict shotgun_pc_data: Pipeline Configuration entity with
            fields ``plugin_ids``, ``sg_plugin_ids``, ``project`` and ``project.id``.
        :returns: True if the pipeline is a centralized pipeline configuration, False otherwise.
        """
        if shotgun_pc_data.get("plugin_ids") or shotgun_pc_data.get("sg_plugin_ids"):
            return False
        if self._project_id is None:
            return shotgun_pc_data["project"] is None
        elif shotgun_pc_data["project"] is None:
            return False
        else:
            return shotgun_pc_data["project"]["id"] == self._project_id

    def _matches_current_plugin_id(self, shotgun_pc_data):
        """
        Checks if a pipeline configuration matches the plugin id associated with
        the resolver.

        Patterns can be comma separated and glob style patterns.
        Examples:

            - basic.nuke, basic.maya
            - basic.*, rv_review

        :param dict shotgun_pc_data: Pipeline Configuration entity with
            fields ``plugin_ids``, ``sg_plugin_ids``.
        :return: True if matching false if not
        """

        # resolve plugins ids in so we first look at the new field and then at the legacy one.
        plugin_ids = shotgun_pc_data.get("plugin_ids") or shotgun_pc_data.get(
            "sg_plugin_ids"
        )

        if plugin_ids is None or self._plugin_id is None:
            return False

        # first split by comma and strip whitespace
        patterns = [chunk.strip() for chunk in plugin_ids.split(",")]

        # glob match each item
        for pattern in patterns:
            if fnmatch.fnmatch(self._plugin_id, pattern):
                log.debug(
                    "Our plugin id '%s' matches pattern '%s'"
                    % (self._plugin_id, plugin_ids)
                )
                return True

        return False
