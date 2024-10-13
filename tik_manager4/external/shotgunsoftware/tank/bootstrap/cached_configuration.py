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
import sys
import traceback
import pprint

from . import constants

from ..descriptor import create_descriptor, Descriptor
from .errors import TankBootstrapError, TankMissingTankNameError

from ..util import filesystem, version

from tank_vendor import yaml
from .configuration import Configuration
from .configuration_writer import ConfigurationWriter
from .. import LogManager

log = LogManager.get_logger(__name__)


class CachedConfiguration(Configuration):
    """
    Represents a configuration which is cached in temp space at runtime
    and kept continously up to date, usually through the means of
    automatic updates.
    """

    def __init__(
        self,
        path,
        sg,
        descriptor,
        project_id,
        plugin_id,
        pipeline_config_id,
        bundle_cache_fallback_paths,
    ):
        """
        :param path: ShotgunPath object describing the path to this configuration
        :param sg: Shotgun API instance
        :param descriptor: ConfigDescriptor for the associated config
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
        """
        super(CachedConfiguration, self).__init__(path, descriptor)
        self._path = path
        self._sg_connection = sg
        self._descriptor = descriptor
        self._project_id = project_id
        self._plugin_id = plugin_id
        self._pipeline_config_id = pipeline_config_id
        self._bundle_cache_fallback_paths = bundle_cache_fallback_paths

        self._config_writer = ConfigurationWriter(self._path, self._sg_connection)

    def __str__(self):
        """
        User friendly representation of the config
        """
        return str(self._descriptor)

    def __repr__(self):
        """
        Low level representation of the config.
        """
        return "<Config with id %s, project id %s, id %s and base %r>" % (
            self._pipeline_config_id,
            self._project_id,
            self._plugin_id,
            self._descriptor,
        )

    def verify_required_shotgun_fields(self):
        """
        Checks so that all shotgun fields required by the configuration
        are present and valid.

        Depending on the configuration, different checks are carried out.

        For configurations using the template and schema system,
        (e.g. has a roots.yml config file set),
        checks are carried out to ensure Project.tank_name and
        local storages are correctly set up.

        This will download the config into the bundle cache if not already
        done.

        :raises: :class:`TankBootstrapError` if checks fail.
        """
        if self._project_id is None:
            # site configuration. Nothing to check
            return

        # make sure the config is locally available.
        self._descriptor.ensure_local()

        log.debug(
            "Verifying that all necessary PTR data is "
            "available in order for config %s to run..." % self
        )

        # ---- verify any defined storage roots for this configuration

        storage_roots = self._descriptor.storage_roots

        # no required storages for this configuration
        if not storage_roots:
            return

        if not storage_roots.required_roots:
            # the storage roots definition file exists, but no storage defined
            # within. might be a placeholder file. treat it as though the file
            # does not exist.
            return

        # ---- validate the storage roots

        log.debug(
            "Detected storage roots definition file %s with roots %s"
            % (storage_roots.roots_file, storage_roots.required_roots)
        )

        (_, unmapped_roots) = storage_roots.get_local_storages(self._sg_connection)

        # get a list of all defined storage roots without a corresponding PTR
        # local storage defined
        if unmapped_roots:
            raise TankBootstrapError(
                "This configuration defines one or more storage roots that can "
                "not be mapped to a local storage defined in Flow Production Tracking. Please "
                "update the roots.yml file in this configuration to correct "
                "this issue. Roots file: '%s'. Unmapped storage roots: %s."
                % (storage_roots.roots_file, ", ".join(unmapped_roots))
            )

        # ---- Ensure tank_name is defined for the project

        log.debug("Ensuring that current project has a tank_name field...")
        proj_data = self._sg_connection.find_one(
            "Project", [["id", "is", self._project_id]], ["tank_name"]
        )
        if proj_data["tank_name"] is None:
            raise TankMissingTankNameError(
                "The configuration requires you to specify a value for the project's "
                "tank_name field in Flow Production Tracking."
            )

    def status(self):
        """
        Compares the actual configuration installed on disk against the
        associated configuration described by the descriptor passed in via
        the class constructor.

        :returns: LOCAL_CFG_UP_TO_DATE, LOCAL_CFG_MISSING,
                  LOCAL_CFG_DIFFERENT, or LOCAL_CFG_INVALID
        """
        log.debug("Checking status of %r" % self)

        # Pass 1:
        # first check if there is any config at all
        sg_config_folder = os.path.join(self._path.current_os, "config")
        if not os.path.exists(sg_config_folder):
            return self.LOCAL_CFG_MISSING

        if self._config_writer.is_transaction_pending():
            return self.LOCAL_CFG_INVALID

        # Pass 2:
        # local config exists. See if it is up to date.
        # get the path to a potential config metadata file
        config_info_file = self._config_writer.get_descriptor_metadata_file()

        if not os.path.exists(config_info_file):
            # not sure what version this is.
            return self.LOCAL_CFG_INVALID

        try:
            with open(config_info_file, "rt") as fh:
                data = yaml.load(fh, Loader=yaml.FullLoader)
                deploy_generation = data["deploy_generation"]
                descriptor_dict = data["config_descriptor"]
        except Exception as e:
            # yaml info not valid.
            log.warning(
                "Cannot parse file '%s' - ignoring. Error: %s" % (config_info_file, e)
            )
            return self.LOCAL_CFG_INVALID

        if deploy_generation != constants.BOOTSTRAP_LOGIC_GENERATION:
            # different format or logic of the deploy itself.
            # trigger a redeploy
            log.debug(
                "Config was installed with a different generation of the logic. "
                "Was expecting %s but got %s.",
                constants.BOOTSTRAP_LOGIC_GENERATION,
                deploy_generation,
            )
            return self.LOCAL_CFG_DIFFERENT

        if descriptor_dict != self._descriptor.get_dict():
            log.debug(
                "Local Config %r does not match "
                "associated descriptor %r"
                % (descriptor_dict, self._descriptor.get_dict())
            )
            return self.LOCAL_CFG_DIFFERENT

        elif not self._descriptor.is_immutable():
            # our desired configuration's descriptor matches
            # the config that is already installed however the descriptor
            # reports that it is not immutable, e.g. it can change at any
            # point (e.g like a dev or path descriptor). Assume a worst case
            # in this case - that the config that is cached locally is
            # not the same as the source descriptor it is based on.
            log.debug(
                "Your configuration contains dev or path descriptors. "
                "Triggering full config rebuild."
            )

            return self.LOCAL_CFG_DIFFERENT

        else:
            log.debug("Local config is up to date")
            return self.LOCAL_CFG_UP_TO_DATE

    def update_configuration(self):
        """
        Ensure that the configuration is up to date with the one
        given by the associated descriptor.

        This method fails gracefully and attempts to roll back to a
        stable state on failure.
        """

        self._config_writer.start_transaction()

        # stow away any previous versions of core and config folders
        try:
            # Move to backup needs to undo changes when failing because we need to put the configuration
            # in a usable state.
            (config_backup_path, core_backup_path) = self._config_writer.move_to_backup(
                undo_on_error=True
            )
        except Exception as e:
            log.exception(
                "Unexpected error while making a backup of the configuration. Toolkit will use the "
                "original configuration."
            )
            return

        self._config_writer.ensure_project_scaffold()
        # copy the configuration into place
        try:

            # make sure the config is locally available.

            # Do not separate these three lines of code or reorder them.
            # In order to make sure the bootstrap hook is invoked ASAP, we should
            # first make sure the config is local, then automatically instantiate
            # the bootstrap hook and finally download the core with that hook if
            # possible.
            self._descriptor.ensure_local()
            self._try_initialize_configuration_cacher()
            core_descriptor = self._ensure_core_local()

            # Log information about the core being setup with this config.
            self._log_core_information(core_descriptor)

            # compatibility checks
            self._verify_descriptor_compatible()
            # v1 of the lean_config allows to run the config from the bundle cache.
            if (
                self._descriptor.get_associated_core_feature_info(
                    "bootstrap.lean_config.version", 0
                )
                < 1
            ):
                # Old-style config, so copy the contents inside it.
                self._descriptor.copy(os.path.join(self._path.current_os, "config"))

            # if the config has a local bundle cache folder, append it to the
            # list of fallback paths. this allows bundles to be included with
            # the config, making it self contained and not requiring additional
            # bundle downloads
            local_bundle_cache_path = os.path.join(
                self._descriptor.get_config_folder(), constants.BUNDLE_CACHE_FOLDER_NAME
            )
            if os.path.exists(local_bundle_cache_path):
                log.debug(
                    "Local bundle cache found in config. "
                    "Adding local bundle cache as fallback path: %s"
                    % (local_bundle_cache_path,)
                )
                self._bundle_cache_fallback_paths.append(local_bundle_cache_path)
            else:
                log.debug("No local bundle cache found in config.")

            # write out config files
            self._config_writer.write_install_location_file()
            self._config_writer.write_config_info_file(self._descriptor)
            self._config_writer.write_shotgun_file(self._descriptor)
            self._config_writer.write_pipeline_config_file(
                self._pipeline_config_id,
                self._project_id,
                self._plugin_id,
                self._bundle_cache_fallback_paths,
                self._descriptor,
            )

            # make sure roots file reflects current paths
            self._config_writer.update_roots_file(self._descriptor)

            # and lastly install core
            self._config_writer.install_core(core_descriptor)

        except Exception as e:

            log.debug(
                "An exception was raised when trying to install the config descriptor %r. "
                "Exception traceback details: %s"
                % (self._descriptor.get_uri(), traceback.format_exc())
            )

            # step 1 - clear core and config locations
            log.debug("Cleaning out faulty config location...")
            # we're purposefully moving the bad pipeline configuration out of the way so we can restore
            # the original one, so move the failed one to backup so it can hopefully be debugged in the future
            # and restore the original one.
            self._config_writer.move_to_backup(undo_on_error=False)
            # step 2 - recover previous core and backup
            if config_backup_path is None or core_backup_path is None:
                # there is nothing to restore!
                log.error(
                    "Failed to install configuration %s. Error: %s. "
                    "Cannot continue." % (self._descriptor.get_uri(), e)
                )
                raise TankBootstrapError(
                    "Configuration could not be installed: %s." % e
                )

            else:
                # ok to restore

                log.error(
                    "Failed to install configuration %s. Will continue with "
                    "the previous version instead. Error reported: %s"
                    % (self._descriptor.get_uri(), e)
                )

                log.debug("Restoring previous config %s" % config_backup_path)
                filesystem.copy_folder(
                    config_backup_path, os.path.join(self._path.current_os, "config")
                )
                log.debug("Previous config restore complete...")

                log.debug("Restoring previous core %s" % core_backup_path)
                filesystem.copy_folder(
                    core_backup_path,
                    os.path.join(self._path.current_os, "install", "core"),
                )
                log.debug("Previous core restore complete...")
        else:
            # remove backup folders now that the update has completed successfully
            # note: config_path points at a config folder inside a timestamped
            # backup folder. It's this parent folder we want to clean up.
            self._cleanup_backup_folders(
                os.path.dirname(config_backup_path) if config_backup_path else None,
                core_backup_path,
            )
            log.debug("Latest backup cleanup complete.")

        # @todo - prime caches (yaml, path cache)

        # make sure tank command and interpreter files are up to date
        self._config_writer.create_tank_command()

        self._config_writer.end_transaction()

    def _ensure_core_local(self):
        """
        Ensures that the core for the current config has been cached to disk.

        :returns: The core descriptor for the current config.
        :rtype: :class:`~sgtk.descriptor.CoreDescriptor`
        """

        if not self._descriptor.associated_core_descriptor:
            log.debug(
                "Config does not have a core/core_api.yml file to define which core to use. "
                "Will use the latest approved core in the app store."
            )
            core_descriptor = create_descriptor(
                self._sg_connection,
                Descriptor.CORE,
                constants.LATEST_CORE_DESCRIPTOR,
                fallback_roots=self._bundle_cache_fallback_paths,
                resolve_latest=True,
            )
        else:
            # we have an exact core descriptor. Get a descriptor for it
            log.debug(
                "Config has a specific core defined in core/core_api.yml: %s"
                % self._descriptor.associated_core_descriptor
            )
            core_descriptor = self._descriptor.resolve_core_descriptor()

        # Look in the config if there is a create_descriptor hook.
        if core_descriptor.exists_local() is False:
            self._download_bundle(core_descriptor)

        return core_descriptor

    def _verify_descriptor_compatible(self):
        """
        Ensures the config we're booting into understands the newer Shotgun descriptor.
        """
        # if it's a shotgun descriptor type using id, ensure
        # that the core we are switching *to* is more recent than 18.120
        descriptor_dict = self._descriptor.get_dict()
        if descriptor_dict["type"] == "shotgun" and "id" in descriptor_dict:
            if self._descriptor.associated_core_version_less_than("v0.18.120"):
                raise TankBootstrapError(
                    "Configurations uploaded to PTR must use core API "
                    "version v0.18.120 or later. Please check the "
                    "core/core_api.yml file in your configuration."
                )

    def _log_core_information(self, core_information):
        """
        Logs features from core we're about to bootstrap into. This is useful for QA.
        """
        try:
            features = core_information.get_features_info()
            log.debug(
                "The core '%s' associated with '%s' has the following feature information:",
                core_information,
                self._descriptor,
            )
            if features:
                log.debug(pprint.pformat(features))
            else:
                log.debug("This version of core can't report features.")
        except Exception as ex:
            # Do not let an error in here trip the bootstrap, but do report.
            log.warning(
                "The core '%s' associated with '%s' couldn't report its features: %s.",
                core_information,
                self._descriptor,
                ex,
            )

    def cache_bundles(self, pipeline_configuration, engine_constraint, progress_cb):
        """
        Caches bundles from the configuration.

        If ``engine_constraint`` is set, only the bundles for that engine instance will be cached.

        :param pipeline_configuration: PipelineConfiguration we're bootstrapping into.
        :param engine_constraint: Name of the engine to constrain the caching to.
        :param progress_cb: Callback to invoke to report progress on bundle caching. The expected
            signature is: ``def progress_cb(message, current_bundle_idx, nb_total_bundles)``

        """
        log.debug("Checking that all bundles are cached locally...")

        if engine_constraint:
            # Download and cache the sole config dependencies needed to run the engine being started,
            log.debug(
                "caching_policy is CACHE_SPARSE - only check items associated with %s"
                % engine_constraint
            )
        else:
            # download and cache the entire config
            log.debug(
                "caching_policy is CACHE_FULL - will download all items defined in the config"
            )

        # Reinitialize the configuration cacher so we use the new swapped core's.
        self._try_initialize_configuration_cacher()

        descriptors = {}
        # pass 1 - populate list of all descriptors
        for env_name in pipeline_configuration.get_environments():
            env_obj = pipeline_configuration.get_environment(env_name)
            for engine in env_obj.get_engines():
                if engine_constraint is None or engine == engine_constraint:
                    descriptor = env_obj.get_engine_descriptor(engine)
                    descriptors[descriptor.get_uri()] = descriptor
                    for app in env_obj.get_apps(engine):
                        descriptor = env_obj.get_app_descriptor(engine, app)
                        descriptors[descriptor.get_uri()] = descriptor

            for framework in env_obj.get_frameworks():
                descriptor = env_obj.get_framework_descriptor(framework)
                descriptors[descriptor.get_uri()] = descriptor

        # pass 2 - download all apps
        for idx, descriptor in enumerate(descriptors.values()):
            if not descriptor.exists_local():
                message = "Downloading %s (%s of %s)..." % (
                    descriptor,
                    idx + 1,
                    len(descriptors),
                )
                progress_cb(message, idx, len(descriptors))
                try:
                    self._download_bundle(descriptor)
                except Exception as e:
                    log.error(
                        "Downloading %r failed to complete successfully. This bundle will be skipped.",
                        e,
                    )
                    log.exception(e)
            else:
                message = "Checking %s (%s of %s)." % (
                    descriptor,
                    idx + 1,
                    len(descriptors),
                )
                log.debug(
                    "%s exists locally at '%s'.", descriptor, descriptor.get_path()
                )
                progress_cb(message, idx, len(descriptors))

    def _cleanup_backup_folders(
        self, config_backup_folder_path, core_backup_folder_path
    ):
        """
        Cleans up backup folders generated by a call to the update_configuration method

        :param config_backup_folder_path: Path to the configuration backup folder to be deleted
                                          or None.
        :param core_backup_folder_path:   Path to the core backup folder to be deleted or None.
        """
        for path in [config_backup_folder_path, core_backup_folder_path]:
            if path:
                try:
                    filesystem.safe_delete_folder(path)
                    log.debug("Deleted backup folder: %s", path)
                except Exception as e:
                    log.warning(
                        "Failed to clean up temporary backup folder '%s': %s"
                        % (path, e)
                    )

    def _try_initialize_configuration_cacher(self):
        """
        Try to import the configuration cacher.

        This will import the one available with the currently in use Toolkit core, if one is
        available.
        """
        try:
            from sgtk.bootstrap.bundle_downloader import BundleDownloader

            self._bundle_downloader = BundleDownloader(
                self._sg_connection, self._pipeline_config_id, self._descriptor
            )
        except ImportError:
            self._bundle_downloader = None

    def _download_bundle(self, descriptor):
        """
        Downloads the bundle through the BundleDownloader if available.

        :param descriptor: Descriptor of the bundle to download.
        """
        # If we don't have any cacher, this is because we're using an older core.
        # In that case, use the download_local method directly on the descriptor.
        if self._bundle_downloader:
            self._bundle_downloader.download_bundle(descriptor)
        else:
            descriptor.download_local()
