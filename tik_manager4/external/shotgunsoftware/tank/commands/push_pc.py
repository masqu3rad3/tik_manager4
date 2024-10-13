# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from ..util import filesystem
from . import constants
from ..errors import TankError
from ..pipelineconfig import PipelineConfiguration

from . import console_utils

from .action_base import Action

from ..util import ShotgunPath

import os
import datetime
import shutil
from tank_vendor.six.moves import input

# Core configuration files which are associated with the core API installation and not
# the pipeline configuration.
CORE_API_FILES = [
    "interpreter_Linux.cfg",
    "interpreter_Windows.cfg",
    "interpreter_Darwin.cfg",
    "shotgun.yml",
]

# Core configuration files which are associated with a particular
# pipeline config and should not be moved.
CORE_PC_FILES = ["install_location.yml", "pipeline_configuration.yml"]


class PushPCAction(Action):
    """
    Action that pushes a config from one pipeline configuration up to its parent
    """

    def __init__(self):
        Action.__init__(
            self,
            "push_configuration",
            Action.TK_INSTANCE,
            (
                "Pushes any configuration changes made here to another configuration. "
                "This is typically used when you have cloned your production configuration "
                "into a staging sandbox, updated the apps in this sandbox and want to push "
                "those updates back to your production configuration."
            ),
            "Configuration",
        )
        # This method can be executed via the API
        self.supports_api = True
        # Parameters we need
        self.parameters = {
            "target_id": {
                "description": "Id of the target Pipeline Configuration to push to.",
                "default": None,
                "type": "int",
            },
            "use_symlink": {
                "description": "Use a symbolic link to copy the data over.",
                "default": False,
                "type": "bool",
            },
        }

        # Just a cache to query PTR only once.
        self._pipeline_configs = None

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """

        self._preflight()
        # validate params and run the action
        self._run(log, **(self._validate_parameters(parameters)))

    def run_interactive(self, log, args):
        """
        Tank command accessor.

        :param log: Standard python logger.
        :param args: Command line args.
        """
        self._preflight()

        if len(args) == 1 and args[0] == "--symlink":
            use_symlink = True
        else:
            use_symlink = False

        current_pc_name = self.tk.pipeline_configuration.get_name()
        current_pc_id = self.tk.pipeline_configuration.get_shotgun_id()

        log.info(
            "This command will push the configuration in the current pipeline configuration "
            "('%s') to another pipeline configuration in the project. By default, the data "
            "will be copied to the target config folder. If pass a --symlink parameter, it will "
            "create a symlink instead." % current_pc_name
        )
        log.info("")
        log.info("Your existing configuration will be backed up.")

        if use_symlink:
            log.info("")
            log.info("A symlink will be used.")
        log.info("")

        log.info("The following pipeline configurations are available to push to:")
        path_hash = {}
        for pc in self._pipeline_configs:
            # skip self
            if pc["id"] == current_pc_id:
                continue
            local_path = ShotgunPath.from_shotgun_dict(pc).current_os
            path_hash[pc["id"]] = local_path
            log.info(" - [%d] %s (%s)" % (pc["id"], pc["code"], local_path))
        log.info("")

        answer = input(
            "Please type in the id of the configuration to push to (ENTER to exit): "
        )
        if answer == "":
            raise TankError("Aborted by user.")
        try:
            target_pc_id = int(answer)
        except:
            raise TankError("Please enter a number!")

        self._run(
            log,
            **(
                self._validate_parameters(
                    {"target_id": target_pc_id, "use_symlink": use_symlink}
                )
            )
        )

    def _preflight(self):
        """
        Performs actions needed in both interactive/non interactive modes.

        Validate we can run a push in the current context.

        :raises: TankError if pushing is invalid.
        """
        # get list of all PCs for this project
        if self.tk.pipeline_configuration.is_site_configuration():
            raise TankError("You can't push the site configuration.")

        if self.tk.pipeline_configuration.is_unmanaged():
            raise TankError("You can't push an unmanaged configuration.")

        project_id = self.tk.pipeline_configuration.get_project_id()

        self._pipeline_configs = self.tk.shotgun.find(
            constants.PIPELINE_CONFIGURATION_ENTITY,
            [["project", "is", {"type": "Project", "id": project_id}]],
            ["code", "linux_path", "windows_path", "mac_path"],
        )

        # We should have at least one pipeline config (the current one)
        # We need a second one to push to, obviously...
        if len(self._pipeline_configs) < 2:
            raise TankError(
                "Only one pipeline configuration for this project! Need at least two "
                "configurations in order to push. Please start by cloning a pipeline "
                "configuration inside of Flow Production Tracking."
            )

    def _run(self, log, target_id, use_symlink=False):
        """
        Push the current pipeline configuration to the one with the given id.

        :param log: A standard logger instance.
        :param int target_id: The target pipeline config id.
        :param bool use_symlink: Whether a symlink should be used
        :raises: TankError on failure.
        """

        # If using symlink, check they are available, which is not the case on
        # Windows.
        if use_symlink and not getattr(os, "symlink", None):
            raise TankError("Symbolic links are not supported on this platform")

        if target_id == self.tk.pipeline_configuration.get_shotgun_id():
            raise TankError(
                "The target pipeline config id must be different from the current one"
            )

        for config in self._pipeline_configs:
            if config["id"] == target_id:
                target_pc_path = ShotgunPath.from_shotgun_dict(config).current_os
                break
        else:
            raise TankError("Id %d is not a valid pipeline config id" % target_id)

        target_pc = PipelineConfiguration(target_pc_path)

        # check that both pcs are using the same core version
        target_core_version = target_pc.get_associated_core_version()
        source_core_version = (
            self.tk.pipeline_configuration.get_associated_core_version()
        )

        if target_core_version != source_core_version:
            raise TankError(
                "The configuration you are pushing to is using Core API %s and "
                "the configuration you are pushing from is using Core API %s. "
                "This is not supported - before pushing the changes, make sure "
                "that both configurations are using the "
                "same Core API!" % (target_core_version, source_core_version)
            )

        # check that there are no dev descriptors
        dev_desc = None
        for env_name in self.tk.pipeline_configuration.get_environments():
            try:
                env = self.tk.pipeline_configuration.get_environment(env_name)
            except Exception as e:
                raise TankError(
                    "Failed to load environment %s,"
                    " run 'tank validate' for more details, got error: %s"
                    % (env_name, e)
                )

            for eng in env.get_engines():
                desc = env.get_engine_descriptor(eng)
                if desc.is_dev():
                    dev_desc = desc
                    break
                for app in env.get_apps(eng):
                    desc = env.get_app_descriptor(eng, app)
                    if desc.is_dev():
                        dev_desc = desc
                        break
        if dev_desc:
            log.warning(
                "Looks like you have one or more dev locations set up in your "
                "configuration! We strongly recommend that you do not use dev locations "
                "in any production based configs. Dev descriptors are for development "
                "purposes only. You can easily switch a dev location using the "
                "'tank switch_app' command."
            )

            if not self._interaction_interface.ask_yn_question("Okay to proceed?"):
                raise TankError("Aborted.")

        date_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        source_path = os.path.join(self.tk.pipeline_configuration.get_path(), "config")
        # Protect ourself against an edge case which happens mostly in unit tests
        # if multiple pushes are attempted within less than a second, which is the
        # granularity of our date_suffix used for uniqueness.
        target_tmp_path = filesystem.get_unused_path(
            os.path.join(target_pc_path, "config.tmp.%s" % date_suffix)
        )
        symlink_path = filesystem.get_unused_path(
            os.path.join(target_pc_path, "config.%s" % date_suffix)
        )
        target_path = os.path.join(target_pc_path, "config")
        target_backup_path = filesystem.get_unused_path(
            os.path.join(target_pc_path, "config.bak.%s" % date_suffix)
        )

        log.debug("Will push the config from %s to %s" % (source_path, target_path))
        log.info("Hold on, pushing config...")

        ##########################################################################################
        # I/O phase
        old_umask = os.umask(0)
        try:

            # copy to temp location
            try:
                # copy everything!
                log.debug("Copying %s -> %s" % (source_path, target_tmp_path))
                filesystem.copy_folder(source_path, target_tmp_path, skip_list=[])

                # If the source and target configurations are both localized, then also copy the
                # core-related api files to the target config. Otherwise, skip them.
                copy_core_related_files = (
                    self.tk.pipeline_configuration.is_localized()
                    and target_pc.is_localized()
                )

                # CORE_PC_FILES are specific to the pipeline configuration so we shouldn't copy them
                if copy_core_related_files:
                    core_files_to_remove = CORE_PC_FILES
                else:
                    core_files_to_remove = CORE_API_FILES + CORE_PC_FILES

                if (
                    self.tk.pipeline_configuration.is_localized()
                    and not target_pc.is_localized()
                ):
                    log.warning(
                        "The source configuration contains a local core but the target "
                        "configuration uses a shared core. The following core-related api "
                        "files will not be copied to the target configuration: "
                        "%s" % CORE_API_FILES
                    )

                # unlock and remove all the special core files from the temp dir so they aren't
                # copied to the target
                for core_file in core_files_to_remove:
                    path = os.path.join(target_tmp_path, "core", core_file)
                    if os.path.exists(path):
                        os.chmod(path, 0o666)
                        log.debug("Removing system file %s" % path)
                        os.remove(path)

                # copy the pc specific special core files from target config to new config temp dir
                # in order to preserve them
                for core_file in CORE_PC_FILES:
                    curr_config_path = os.path.join(target_path, "core", core_file)
                    new_config_path = os.path.join(target_tmp_path, "core", core_file)
                    log.debug(
                        "Copying PC system file %s -> %s"
                        % (curr_config_path, new_config_path)
                    )
                    shutil.copy(curr_config_path, new_config_path)

            except Exception as e:
                raise TankError(
                    "Could not copy into temporary target folder '%s'. The target config "
                    "has not been altered. Check permissions and try again! "
                    "Error reported: %s" % (target_tmp_path, e)
                )

            # backup original config
            created_backup_path = None
            try:
                if os.path.islink(target_path):
                    # If we are symlinked, no need to back up: just delete the
                    # current symlink.
                    # If remove fails, we don't have to worry about restoring the
                    # original `target_path`: if it failed, it is still there...
                    os.remove(target_path)
                else:
                    # Move data to backup folder
                    # Try using os.rename first, which is a lot more efficient than
                    # copying all files over, as it just updates inode tables on Unix.
                    # If it fails, fall back to copying files and deleting them
                    # only after everything was copied over.
                    # We basically replicates what shutil.move does, but we use
                    # shutil.copytree and filesystem.safe_delete_folder to ensure
                    # we only delete data after everything was copied over in the
                    # backup folder.
                    try:
                        os.rename(target_path, target_backup_path)
                        created_backup_path = target_backup_path
                    except OSError as e:
                        log.debug("Falling back on copying folder...:%s" % e)
                        # Didn't work fall back to copying files
                        shutil.copytree(target_path, target_backup_path)
                        # Delete below could fail, but we do have a backup, so flag
                        # it now.
                        created_backup_path = target_backup_path
                        filesystem.safe_delete_folder(target_path)
            except Exception as e:
                raise TankError(
                    "Could not move target folder from '%s' to '%s'. "
                    "Error reported: %s" % (target_path, target_backup_path, e)
                )

            # lastly, move new config into place
            if use_symlink:
                try:
                    # If the symlink path exists, shutil.move will move the
                    # tmp folder inside it, instead of renaming the tmp folder with
                    # the target path, leading to invalid config. So check this
                    # and report it.
                    if os.path.exists(symlink_path):
                        raise RuntimeError(
                            "Target %s folder already exists..." % symlink_path
                        )
                    shutil.move(target_tmp_path, symlink_path)
                    # It seems that when given a basename as the source for the
                    # link, symlink creates the link in the target directory, so
                    # this works without having to change the current directory?
                    os.symlink(os.path.basename(symlink_path), target_path)
                except Exception as e:
                    raise TankError(
                        "Could not move new config folder from '%s' to '%s' or create symlink."
                        "Error reported: %s" % (target_tmp_path, symlink_path, e)
                    )
            else:
                try:
                    # If the target path still exists, shutil.move will move the
                    # tmp folder inside it, instead of renaming the tmp folder with
                    # the target path, leading to invalid config. So check this
                    # and report it.
                    if os.path.exists(target_path):
                        raise RuntimeError(
                            "Target %s folder already exists..." % target_path
                        )
                    shutil.move(target_tmp_path, target_path)
                except Exception as e:
                    raise TankError(
                        "Could not move new config folder from '%s' to '%s'. "
                        "Error reported: %s" % (target_tmp_path, target_path, e)
                    )

        finally:
            os.umask(old_umask)
            if created_backup_path:
                log.info(
                    "Your old configuration has been backed up "
                    "into the following folder: %s" % created_backup_path
                )

        ##########################################################################################
        # Post Process Phase

        # now download all apps
        log.info("Checking if there are any apps that need downloading...")
        for env_name in target_pc.get_environments():
            env = target_pc.get_environment(env_name)
            for eng in env.get_engines():
                desc = env.get_engine_descriptor(eng)
                if not desc.exists_local():
                    log.info("Downloading Engine %s..." % eng)
                    desc.download_local()
                for app in env.get_apps(eng):
                    desc = env.get_app_descriptor(eng, app)
                    if not desc.exists_local():
                        log.info("Downloading App %s..." % app)
                        desc.download_local()

        log.info("")
        log.info("Push Complete!")
        log.info("")
