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
import sys
import datetime

from . import constants

from ..descriptor import Descriptor, create_descriptor, is_descriptor_version_missing

from ..util import filesystem
from ..util import StorageRoots
from ..util.shotgun import connection
from ..util.move_guard import MoveGuard
from ..util import is_macos, is_windows

from tank_vendor import yaml

from .. import LogManager

log = LogManager.get_logger(__name__)


class ConfigurationWriter(object):
    """
    Class used to write and update Toolkit configurations on disk.
    """

    _TRANSACTION_START_FILE = "update_start.txt"
    _TRANSACTION_END_FILE = "update_end.txt"

    def __init__(self, path, sg):
        """
        Constructor.

        :param path: ShotgunPath object describing the path to this configuration
        :param sg: Shotgun API instance
        """
        self._path = path
        self._sg_connection = sg

    @property
    def path(self):
        """
        Path at which the configuration will be written.

        :returns: Path to the configuration on disk.
        :rtype: :class:`ShotgunPath`
        """
        return self._path

    def ensure_project_scaffold(self):
        """
        Creates all the necessary files on disk for a basic config scaffold.
        """
        config_path = self._path.current_os
        log.debug("Ensuring project scaffold in '%s'..." % config_path)

        filesystem.ensure_folder_exists(config_path)
        filesystem.ensure_folder_exists(os.path.join(config_path, "cache"))

        # Required for files written to the config like pipeline_confguration.yml,
        # shotgun.yml, etc.
        filesystem.ensure_folder_exists(os.path.join(config_path, "config", "core"))

        filesystem.ensure_folder_exists(
            os.path.join(config_path, "install", "config.backup"),
            create_placeholder_file=True,
        )
        filesystem.ensure_folder_exists(
            os.path.join(config_path, "install", "core.backup"),
            create_placeholder_file=True,
        )

    def install_core(self, core_descriptor):
        """
        Install a core into the given configuration.

        This will copy the core API from the given location into
        the configuration, effectively mimicing a localized setup.

        :param core_descriptor: Core descriptor to use to determine core version
        """
        config_root_path = self._path.current_os
        core_target_path = os.path.join(config_root_path, "install", "core")

        log.debug("Copying core into place")
        core_descriptor.copy(core_target_path)

    def get_descriptor_metadata_file(self):
        """
        Returns the path to the metadata file holding descriptor information.

        :return: path
        """
        path = os.path.join(self._path.current_os, "cache", "descriptor_info.yml")
        filesystem.ensure_folder_exists(os.path.dirname(path))
        return path

    def move_to_backup(self, undo_on_error):
        """
        Move any existing config and core to a backup location.

        After this method has been executed, there is no config and
        no install/core folder present in the configuration scaffold.
        Both have been moved into their respective backup locations.

        :param bool undo_on_error: If True, the move to backup will be undone if there is an error during
            the backup process.

        :returns: (config_backup_path, core_backup_path) where the paths
                  can be None in case nothing was carried over.

        """

        # The move guard's role is to keep track of every move operation that has happened
        # in a given scope and undo all the moves if something went wrong. This feels a lot simpler
        # than having a try/except block as we'd have to have different try/except blocks for different
        # code sections. Its also a great way to avoid having to deal with variables that haven't been
        # defined yet when dealing with the exceptions.
        with MoveGuard(undo_on_error) as guard:
            config_backup_path = None
            core_backup_path = None

            # get backup root location
            config_path = self._path.current_os
            configuration_payload = os.path.join(config_path, "config")

            # timestamp for rollback backup folders
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            if os.path.exists(configuration_payload):

                config_backup_root = os.path.join(
                    config_path, "install", "config.backup"
                )

                # make sure we have a backup folder present
                # sometimes, execution and rollback is so quick that several backup folders
                # are created in a single second. In that case, append a suffix
                config_backup_path = os.path.join(config_backup_root, timestamp)
                counter = 0
                while os.path.exists(config_backup_path):
                    # that backup path already exists. Try another one
                    counter += 1
                    config_backup_path = os.path.join(
                        config_backup_root, "%s.%d" % (timestamp, counter)
                    )

                # now that we have found a spot for our backup, make sure folder exists
                # and then move the existing config *into* this folder.
                filesystem.ensure_folder_exists(config_backup_path)

                log.debug(
                    "Moving config %s -> %s"
                    % (configuration_payload, config_backup_path)
                )
                backup_target_path = os.path.join(
                    config_backup_path, os.path.basename(configuration_payload)
                )
                guard.move(configuration_payload, backup_target_path)
                log.debug("Backup complete.")
                config_backup_path = backup_target_path

            # now back up the core API
            core_payload = os.path.join(config_path, "install", "core")

            if os.path.exists(core_payload):
                core_backup_root = os.path.join(config_path, "install", "core.backup")
                # should not be necessary but just in case.
                filesystem.ensure_folder_exists(core_backup_root)

                # make sure we have a backup folder present
                # sometimes, execution and rollback is so quick that several backup folders
                # are created in a single second. In that case, append a suffix
                core_backup_path = os.path.join(core_backup_root, timestamp)
                counter = 0
                while os.path.exists(core_backup_path):
                    # that backup path already exists. Try another one
                    counter += 1
                    core_backup_path = os.path.join(
                        core_backup_root, "%s.%d" % (timestamp, counter)
                    )

                log.debug("Moving core %s -> %s" % (core_payload, core_backup_path))
                guard.move(core_payload, core_backup_path)
                guard.done()
                log.debug("Backup complete.")
                core_backup_path = core_backup_path

            return (config_backup_path, core_backup_path)

    @filesystem.with_cleared_umask
    def create_tank_command(self, executable=sys.executable, prefix=sys.prefix):
        """
        Create a tank command for this configuration.

        The tank command binaries will be copied from the current core distribution
        The interpreter_xxx.cfg files will be created based on the ``sys.executable``.

        :param current_interpreter: Path to the current interpreter. Defaults to sys.executable.
        """
        log.debug("Installing tank command...")

        # First set up the interpreter_xxx files needed for the tank command
        # default to the PTR desktop app python. We want those defaults, even with descriptor
        # based pipeline configurations, because from a descriptor based pipeline configuration
        # we might want call setup_project, which will copy the interpreter files. So as a
        # convenience we'll pre-fill those files with an interpreter we know is available on all
        # platforms.
        executables = dict(
            Linux=constants.DESKTOP_PYTHON_LINUX,
            Darwin=constants.DESKTOP_PYTHON_MAC,
            Windows=constants.DESKTOP_PYTHON_WIN,
        )

        # FIXME: This is a really bad hack. We're looking to see if we are running inside the
        # Shogun Desktop and if we are then we're using the Python that is package with it.
        #
        # The reason we are doing this is because we need the interpreter files
        # written out during bootstrapping to be using the ones from the PTR desktop app.
        #
        # We could have introduced a way on the ToolkitManager to specify the interpreter
        # to use for the current platform for descriptor based configuration, but we're trying
        # to kill the interpreter files in the first place mid-term, so introducing an API
        # that allows the caller to specify which one to use feels backwards in the first place.
        #
        # This feels like the lesser of two evils, even tough as I type this I've thrown
        # up a bit in my mouth.

        # Figures out which is the current Python interpreter.
        # If we're in the PTR desktop app
        if os.path.split(executable)[1].lower().startswith("shotgun"):
            log.debug("PTR desktop app process detected.")
            # We'll use the builtin Python.
            if is_macos():
                current_interpreter = os.path.join(prefix, "bin", "python")
            elif is_windows():
                current_interpreter = os.path.join(prefix, "python.exe")
            else:
                current_interpreter = os.path.join(prefix, "bin", "python")
        elif os.path.split(executable)[1].lower().startswith("python"):
            # If we're in a Python executable, we should use that.
            current_interpreter = executable
        else:
            current_interpreter = None

        # Sets the interpreter in the current OS, we'll leave the defaults for the other platforms.
        if current_interpreter:
            if is_macos():
                executables["Darwin"] = current_interpreter
            elif is_windows():
                executables["Windows"] = current_interpreter
            else:
                executables["Linux"] = current_interpreter

        if current_interpreter:
            log.debug("Current OS interpreter will be %s.", current_interpreter)
        else:
            log.debug("Current OS interpreter will be the default PTR desktop app location.")

        config_root_path = self._path.current_os

        # Write out missing files.
        for platform in executables:
            sg_config_location = os.path.join(
                config_root_path, "config", "core", "interpreter_%s.cfg" % platform
            )
            # If the interpreter file already existed in the configuration, we won't overwrite it.
            if os.path.exists(sg_config_location):
                log.debug(
                    "Interpreter file %s already exists, leaving as is.",
                    sg_config_location,
                )
                continue
            # create new file
            with open(sg_config_location, "wt") as fh:
                fh.write(executables[platform])

        # now deploy the actual tank command
        core_target_path = os.path.join(config_root_path, "install", "core")
        root_binaries_folder = os.path.join(core_target_path, "setup", "root_binaries")
        for file_name in os.listdir(root_binaries_folder):
            src_file = os.path.join(root_binaries_folder, file_name)
            tgt_file = os.path.join(config_root_path, file_name)
            # clear out any existing files
            filesystem.safe_delete_file(tgt_file)
            # and copy new one into place
            log.debug("Installing tank command %s -> %s" % (src_file, tgt_file))
            filesystem.copy_file(src_file, tgt_file, 0o775)

    def write_install_location_file(self):
        """
        Writes the install location file
        """
        config_path = self._path.current_os

        # write the install_location file for our new setup
        sg_code_location = os.path.join(
            config_path, "config", "core", "install_location.yml"
        )

        if os.path.exists(sg_code_location):
            # We want to log that we're overwriting an existing file, but this file
            # is almost exclusively auto generated, so we can do it as a debug.
            log.debug(
                "The file 'core/install_location.yml' exists in the configuration "
                "but will be overwritten with an auto generated file."
            )

        with filesystem.auto_created_yml(sg_code_location) as fh:

            fh.write("# This file reflects the paths in the pipeline\n")
            fh.write("# configuration defined for this project.\n")
            fh.write("\n")

            locations = {}
            locations["Windows"] = self._path.windows
            locations["Darwin"] = self._path.macosx
            locations["Linux"] = self._path.linux

            yaml.safe_dump(locations, fh, default_flow_style=False)

    def write_config_info_file(self, config_descriptor):
        """
        Writes a cache file with info about where the config came from.

        :param config_descriptor: Config descriptor object
        """
        config_info_file = self.get_descriptor_metadata_file()

        with filesystem.auto_created_yml(config_info_file) as fh:
            fh.write("# This file contains metadata describing what exact version\n")
            fh.write("# Of the config that was downloaded from Flow Production Tracking\n")
            fh.write("\n")
            fh.write("# Below follows details for the sg attachment that is\n")
            fh.write("# reflected within this local configuration.\n")
            fh.write("\n")

            metadata = {}
            # bake in which version of the deploy logic was used to push this config
            metadata["deploy_generation"] = constants.BOOTSTRAP_LOGIC_GENERATION
            # and include details about where the config came from
            metadata["config_descriptor"] = config_descriptor.get_dict()

            # write yaml
            yaml.safe_dump(metadata, fh)

    def write_shotgun_file(self, descriptor):
        """
        Writes config/core/shotgun.yml
        """

        source_config_sg_file = os.path.join(
            descriptor.get_path(), "core", constants.CONFIG_SHOTGUN_FILE
        )

        dest_config_sg_file = os.path.join(
            self._path.current_os, "config", "core", constants.CONFIG_SHOTGUN_FILE
        )

        # If there is a shotgun.yml file at the source location, read it
        # in as the default metadata.
        #
        # This allows to centralize proxy settings in a shotgun.yml that
        # gets distributed every time a configuration is written.
        if os.path.exists(source_config_sg_file):
            log.debug("shotgun.yml found in the config at '%s'.", source_config_sg_file)
            with open(source_config_sg_file, "rb") as fh:
                metadata = yaml.load(fh, Loader=yaml.FullLoader)
        else:
            log.debug(
                "File '%s' does not exist in the config. shotgun.yml will only contain the host.",
                source_config_sg_file,
            )
            metadata = {}

        with filesystem.auto_created_yml(dest_config_sg_file) as fh:
            # ensure the metadata has the host set. We shouldn't assume the shotgun.yml
            # file that can be distributed with the config has the host set, as it
            # could be used on two different Shotgun servers, for example a production
            # server and a staging server that are both hosted locally.
            metadata["host"] = connection.sanitize_url(self._sg_connection.base_url)
            # write yaml
            yaml.safe_dump(metadata, fh)

        log.debug("Wrote %s", dest_config_sg_file)

    def write_pipeline_config_file(
        self,
        pipeline_config_id,
        project_id,
        plugin_id,
        bundle_cache_fallback_paths,
        source_descriptor,
    ):
        """
        Writes out the the pipeline configuration file config/core/pipeline_config.yml

        This will populate all relevant parameters required for a toolkit runtime setup.
        Project and pipeline configuration names will be resolved from Shotgun.

        :param pipeline_config_id: Pipeline config id or None for an unmanaged config.
        :param project_id: Project id or None for the site config or for a baked config.
        :param plugin_id: Plugin id string to identify the scope for a particular plugin
                          or integration. For more information,
                          see :meth:`~sgtk.bootstrap.ToolkitManager.plugin_id`. For
                          non-plugin based toolkit projects, this value is None.
        :param bundle_cache_fallback_paths: List of bundle cache fallback paths.
        :param source_descriptor: Descriptor object used to identify
            which descriptor the pipeline configuration originated from.
            For configurations where this source may not be directly accessible,
            (e.g. baked configurations), this can be set to ``None``.

        :returns: Path to the configuration file that was written out.
        """
        if project_id:
            # Look up the project name via the project id
            log.debug("Checking project in Flow Production Tracking...")
            sg_data = self._sg_connection.find_one(
                "Project", [["id", "is", project_id]], ["tank_name"]
            )

            # When the given project id cannot be found, raise a meaningful exception.
            if not sg_data:
                msg = "Unknown project id %s" % project_id
                log.debug("Raising ValueError('%s')" % msg)
                raise ValueError(msg)

            project_name = sg_data["tank_name"] or constants.UNNAMED_PROJECT_NAME
        else:
            project_name = constants.UNNAMED_PROJECT_NAME

        # the pipeline config metadata
        # resolve project name and pipeline config name from shotgun.
        if pipeline_config_id:
            # look up pipeline config name and project name via the pc
            log.debug("Checking pipeline config in Flow Production Tracking...")

            sg_data = self._sg_connection.find_one(
                constants.PIPELINE_CONFIGURATION_ENTITY_TYPE,
                [["id", "is", pipeline_config_id]],
                ["code"],
            )
            pipeline_config_name = (
                sg_data["code"] or constants.UNMANAGED_PIPELINE_CONFIG_NAME
            )
        elif project_id:
            pipeline_config_name = constants.UNMANAGED_PIPELINE_CONFIG_NAME
        else:
            # this is either a site config or a baked config.
            # in the latter case, the project name will be overridden at
            # runtime (along with many other parameters).
            project_name = "Site"
            pipeline_config_name = constants.UNMANAGED_PIPELINE_CONFIG_NAME

        pipeline_config_content = {
            "pc_id": pipeline_config_id,
            "pc_name": pipeline_config_name,
            "project_id": project_id,
            "project_name": project_name,
            "plugin_id": plugin_id,
            "published_file_entity_type": "PublishedFile",
            "use_bundle_cache": True,
            "bundle_cache_fallback_roots": bundle_cache_fallback_paths,
            "use_shotgun_path_cache": True,
        }

        if source_descriptor:
            pipeline_config_content["source_descriptor"] = source_descriptor.get_dict()

        # write pipeline_configuration.yml
        pipeline_config_path = os.path.join(
            self._path.current_os, "config", "core", constants.PIPELINECONFIG_FILE
        )

        if os.path.exists(pipeline_config_path):
            # warn if this file already exists
            log.warning(
                "The file 'core/%s' exists in the configuration "
                "but will be overwritten with an auto generated file."
                % constants.PIPELINECONFIG_FILE
            )

        with filesystem.auto_created_yml(pipeline_config_path) as fh:
            yaml.safe_dump(pipeline_config_content, fh)

        return pipeline_config_path

    def update_roots_file(self, config_descriptor):
        """
        Updates roots.yml based on local storage defs in shotgun.

        :param config_descriptor: Config descriptor object
        """

        config_folder = os.path.join(self._path.current_os, "config")
        StorageRoots.write(
            self._sg_connection, config_folder, config_descriptor.storage_roots
        )

    def is_transaction_pending(self):
        """
        Checks if the configuration was previously in the process of being updated but then stopped.

        .. note::
            Configurations written with previous versions of Toolkit are assumed to completed.

        :returns: True if the configuration was not finished being written on disk, False if it was.
        """

        # Check if the transaction folder exists...
        is_started = os.path.exists(
            self._get_state_file_name(self._TRANSACTION_START_FILE)
        )
        is_ended = os.path.exists(self._get_state_file_name(self._TRANSACTION_END_FILE))

        if is_started and not is_ended:
            log.warning("It seems the configuration was not written properly on disk.")
            return True
        if is_started and is_ended:
            log.debug("Configuration was written properly on disk.")
            return False
        if not is_started and is_ended:
            log.error("It seems the configuration is in an unconsistent state.")
            return True

        log.debug("Configuration doesn't have transaction markers.")
        return False

    def start_transaction(self):
        """
        Wipes the transaction marker from the configuration.
        """
        log.debug("Starting configuration update transaction.")
        filesystem.ensure_folder_exists(os.path.join(self._path.current_os, "cache"))
        self._delete_state_file(self._TRANSACTION_END_FILE)
        self._write_state_file(self._TRANSACTION_START_FILE)

    def _write_state_file(self, file_name):
        """
        Writes a transaction file.
        """
        with open(self._get_state_file_name(file_name), "w") as fw:
            fw.writelines(["File written at %s." % datetime.datetime.now()])

    def _delete_state_file(self, file_name):
        """
        Deletes a transaction file.
        """
        filesystem.safe_delete_file(self._get_state_file_name(file_name))

    def _get_state_file_name(self, file_name):
        """
        Retrieves the path to a transaction file.
        """
        return os.path.join(self._path.current_os, "cache", file_name)

    def end_transaction(self):
        """
        Creates a transaction marker in the configuration indicating is has been completely written
        to disk.
        """
        # Write back the coherency token.
        log.debug("Ending configuration update transaction.")
        self._write_state_file(self._TRANSACTION_END_FILE)

    def _get_configuration_transaction_filename(self):
        """
        :returns: Path to the file which will be used to track configuration validity.
        """
        return os.path.join(self._get_configuration_transaction_folder(), "done")
