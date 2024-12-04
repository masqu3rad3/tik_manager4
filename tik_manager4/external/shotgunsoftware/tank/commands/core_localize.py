# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# make sure that py25 has access to with statement
from __future__ import with_statement

import os
import sys
import shutil
import datetime

from ..errors import TankError
from ..util import filesystem
from ..util.version import is_version_older
from .action_base import Action
from .. import pipelineconfig_utils
from .. import pipelineconfig_factory
from tank_vendor import six
from tank_vendor.shotgun_api3.lib import sgsix

# these are the items that need to be copied across
# when a configuration is upgraded to contain a core API
CORE_FILES_FOR_LOCALIZE = [
    "shotgun.yml",
    "app_store.yml",
    "interpreter_Darwin.cfg",
    "interpreter_Linux.cfg",
    "interpreter_Windows.cfg",
]


class CoreLocalizeAction(Action):
    """
    Action to localize the Core API
    """

    def __init__(self):
        Action.__init__(
            self,
            "localize",
            Action.TK_INSTANCE,
            (
                "Installs the Core API into your current Configuration. This is typically "
                "done when you want to test a Core API upgrade in an isolated way. If you "
                "want to safely test an API upgrade, first clone your production configuration, "
                "then run the localize command from your clone's tank command."
            ),
            "Admin",
        )

        # this method can be executed via the API
        self.supports_api = True

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        pc_root = self.tk.pipeline_configuration.get_path()
        log.debug("Executing the localize command for %r" % self.tk)
        return do_localize(log, self.tk.shotgun, pc_root, self._interaction_interface)

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        if len(args) != 0:
            raise TankError("This command takes no arguments!")

        pc_root = self.tk.pipeline_configuration.get_path()
        log.debug("Executing the localize command for %r" % self.tk)
        return do_localize(log, self.tk.shotgun, pc_root, self._interaction_interface)


def do_localize(log, sg_connection, target_config_path, interaction_interface):
    """
    Perform the actual localize command.

    :param log: logging object
    :param sg_connection: An open shotgun connection
    :param str target_config_path: Path to the config that should be localized.
    :param interaction_interface: Interface to use to interact with the user
    """

    # the configuration to localize
    target_pipeline_config = pipelineconfig_factory.from_path(target_config_path)

    # the core install location for the current config. this will be resolved to
    # a linked config or the config where the running core lives
    source_config_path = target_pipeline_config.get_install_location()

    log.info("")
    if target_pipeline_config.is_localized():
        # if we're here, there's already a core in the config's install folder
        raise TankError(
            "Looks like your current pipeline configuration already has a "
            "local install of the core!"
        )

    # if a core descriptor is supplied, ensure it is cached locally and use it
    # as the core to localize.
    if pipelineconfig_utils.has_core_descriptor(target_config_path):
        core_descriptor = pipelineconfig_utils.get_core_descriptor(
            target_config_path, sg_connection
        )
        core_descriptor.ensure_local()
        source_core_path = core_descriptor.get_path()
        source_core_version = core_descriptor.get_version()

        log.info(
            "Core descriptor %s, specified in core/core_api.yml, "
            "will be installed." % (core_descriptor.get_uri())
        )

    else:
        # fall back to using the core that exists in the source config
        source_core_path = os.path.join(source_config_path, "install", "core")

        # resolve the version of core
        source_core_version = target_pipeline_config.get_associated_core_version()

        log.info(
            "This will copy the Core API in %s \n"
            "into the Pipeline configuration %s."
            % (source_core_path, target_config_path)
        )

    log.info("")
    # check with user if they wanna continue
    if not interaction_interface.ask_yn_question("Do you want to proceed"):
        # user says no!
        log.info("Operation cancelled.")
        return

    log.debug("About to localize '%s'" % target_config_path)
    log.debug(
        "Associated core is '%s', version %s" % (source_core_path, source_core_version)
    )
    log.debug(
        "The version of core running this code is %s"
        % pipelineconfig_utils.get_currently_running_api_version()
    )

    # proceed with setup
    log.info("")

    # define the install paths for the source and target configs
    source_install_path = os.path.join(source_config_path, "install")
    target_install_path = os.path.join(target_config_path, "install")

    try:

        # ---- Step 1: Localize all bundles...

        if is_version_older(source_core_version, "v0.18.0"):
            # now if we are localizing a pre-0.18 core, it means we are using
            # modern (post 0.18) core code to copy a 0.17 core across into the
            # configuration in this case, the old storage logic for descriptors
            # applies. We handle this by brute forcing it and copying all items
            # across in the install folder.

            log.debug(
                "Using a 0.18 core to localize a 0.17 core. Falling back on "
                "blanket copy of install."
            )

            # copy all the contents of the install location across except for
            # the contents in the core and core.backup folders - these are
            # handled explicitly later on

            for name in os.listdir(source_install_path):

                if name in ["core", "core.backup"]:
                    # skip now and handle separately
                    continue

                if name.startswith(".") or name.startswith("_"):
                    # skip system directories such as __MACOSX and .DS_store
                    continue

                source = os.path.join(source_install_path, name)
                target = os.path.join(target_install_path, name)
                log.info("Localizing the %s folder..." % name)
                filesystem.copy_folder(source, target)

        else:
            # 0.18 descriptor based API implementation

            # First get a list of all bundle descriptors.
            # Key by descriptor uri, which ensures no repetition.
            descriptors = {}
            for env_name in target_pipeline_config.get_environments():

                env_obj = target_pipeline_config.get_environment(env_name)

                for engine in env_obj.get_engines():
                    descriptor = env_obj.get_engine_descriptor(engine)
                    descriptors[descriptor.get_uri()] = descriptor

                    for app in env_obj.get_apps(engine):
                        descriptor = env_obj.get_app_descriptor(engine, app)
                        descriptors[descriptor.get_uri()] = descriptor

                for framework in env_obj.get_frameworks():
                    descriptor = env_obj.get_framework_descriptor(framework)
                    descriptors[descriptor.get_uri()] = descriptor

            for idx, descriptor in enumerate(six.itervalues(descriptors)):
                # print one based indices for more human friendly output
                log.info(
                    "%s/%s: Copying %s..." % (idx + 1, len(descriptors), descriptor)
                )
                descriptor.clone_cache(target_install_path)

        # ---- Step 2: Backup the target core and copy the new core across...

        # construct paths to the installed "core" and "core.backup" folders in
        # the target config
        target_core_path = os.path.join(target_install_path, "core")
        target_core_backup_path = os.path.join(target_install_path, "core.backup")

        log.info("Backing up existing Core API...")

        # timestamped folder name in "core.backup"
        target_core_backup_folder_name = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        # full path to the core backup folder (including timestamped folder)
        target_core_backup_folder_path = os.path.join(
            target_core_backup_path, target_core_backup_folder_name
        )

        # do the actual copy of whatever's currently in "install/core" to the
        # timestampted backup folder
        src_files = filesystem.copy_folder(
            target_core_path, target_core_backup_folder_path
        )

        # clean out the "core" folder
        log.debug("Clearing out core target location...")
        for f in src_files:
            filesystem.safe_delete_file(f)

        log.info("Copying Core %s \nto %s" % (source_core_path, target_core_path))
        filesystem.copy_folder(source_core_path, target_core_path)

        # Step 3: Copy some core config files across.
        log.info("Copying Core configuration files...")
        for fn in CORE_FILES_FOR_LOCALIZE:
            src = os.path.join(source_config_path, "config", "core", fn)
            tgt = os.path.join(target_config_path, "config", "core", fn)
            log.debug("Copy %s -> %s" % (src, tgt))

            # If we're copying any other file than app_store.yml, it is
            # mandatory. If we're copying app_store.yml, only copy it if it
            # exists. This is because when you are localizing a core,
            # app_store.yml might be present or not depending if you are
            # migrating a core configured with a pre Shotgun 6 or post Shotgun 6
            # site. In the latter, AppStore credentials can be retrieved using a
            # session token and therefore we don't need the AppStore credentials
            # to be saved on disk.
            if fn != "app_store.yml" or os.path.exists(src):
                filesystem.copy_file(src, tgt, permissions=0o666)

    except Exception as e:
        log.exception("Could not localize Toolkit API.")
        raise TankError("Could not localize Toolkit API: %s" % e)

    log.info("The Core API was successfully localized.")

    log.info("")
    log.info(
        "Localize complete! " "This pipeline configuration now has an independent API."
    )
    log.info("")
    log.info("")


class ShareCoreAction(Action):
    """
    Action to take a localized core and move it out into an external location on disk.
    """

    def __init__(self):
        Action.__init__(
            self,
            "share_core",
            Action.TK_INSTANCE,
            (
                "When new projects are created, these are often created in a state where each project "
                "maintains its own independent copy of the core API. This command allows you to take "
                "the core for such a project and move it out into a separate location on disk. This "
                "makes it possible to create a shared core, where several projects share a single copy "
                "of the Core API. Note: if you already have a shared Core API that you would like this "
                "configuration to use, instead use the attach_to_core command."
            ),
            "Admin",
        )

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        # note how the current platform's default value is None in order to make that required
        self.parameters["core_path_mac"] = {
            "description": (
                "The path on disk where the core API should be " "installed on Macosx."
            ),
            "default": (None if sgsix.platform == "darwin" else ""),
            "type": "str",
        }

        self.parameters["core_path_win"] = {
            "description": (
                "The path on disk where the core API should be " "installed on Windows."
            ),
            "default": (None if sgsix.platform == "win32" else ""),
            "type": "str",
        }

        self.parameters["core_path_linux"] = {
            "description": (
                "The path on disk where the core API should be " "installed on Linux."
            ),
            "default": (None if sgsix.platform == "linux2" else ""),
            "type": "str",
        }

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """

        # validate params and seed default values
        computed_params = self._validate_parameters(parameters)

        return _run_unlocalize(
            self.tk,
            log,
            computed_params["core_path_mac"],
            computed_params["core_path_win"],
            computed_params["core_path_linux"],
            self._interaction_interface,
            copy_core=True,
        )

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """

        if len(args) != 3:
            log.info("Syntax: share_core linux_path windows_path mac_path")
            log.info("")
            log.info(
                "This command is only relevant for configurations which maintain their "
                "own copy of the Core API (so called localized configurations). For such configurations, "
                "this command will move the embedded core API out into an external location on disk."
            )
            log.info("")
            log.info("You typically need to quote your paths, like this:")
            log.info("")
            log.info(
                '> tank share_core "/mnt/shotgun/studio" "p:\\shotgun\\studio" "/mnt/shotgun/studio"'
            )
            log.info("")
            log.info(
                "If you want to leave a platform blank, just use empty quotes. For example, "
                "if you want a setup which only works on windows, do like this: "
            )
            log.info("")
            log.info('> tank share_core "" "p:\\shotgun\\studio" ""')
            log.info("")
            raise TankError("Please specify three target locations!")

        linux_path = args[0]
        windows_path = args[1]
        mac_path = args[2]

        return _run_unlocalize(
            self.tk,
            log,
            mac_path,
            windows_path,
            linux_path,
            self._interaction_interface,
            copy_core=True,
        )


class AttachToCoreAction(Action):
    """
    Action to take a localized config, discard the built in core and associate it with an existing core.
    """

    def __init__(self):
        Action.__init__(
            self,
            "attach_to_core",
            Action.TK_INSTANCE,
            (
                "When new projects are created, these are often created in a state where each project "
                "maintains its own independent copy of the core API. This command allows you to attach "
                "the configuration to an existing core API installation rather than having it maintain "
                "its own embedded version of the Core API. Note: If you don't have a shared core API "
                "yet, instead use the share_core command."
            ),
            "Admin",
        )

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        # note how the current platform's default value is None in order to make that required
        self.parameters["path"] = {
            "description": "Path to a core you want to attach to.",
            "default": None,
            "type": "str",
        }

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """

        # validate params and seed default values
        computed_params = self._validate_parameters(parameters)

        return self._run_wrapper(log, computed_params["path"])

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """

        if len(args) != 1:
            log.info("Syntax: attach_to_core path_to_core")
            log.info("")
            log.info(
                "This command is only relevant for configurations which maintain their "
                "own copy of the Core API (so called localized configurations). For such configurations, "
                "this command will remove the built-in core and instead attach the configuration to the "
                "specified core API. The core API you are trying to attach to must not be an older version "
                "than the currently associated core API (%s)" % self.tk.version
            )
            log.info("")
            log.info("Example:")
            log.info("")
            log.info("> tank attach_to_core /mnt/shotgun/studio")
            log.info("")
            raise TankError(
                "Please specify the location of the core you would like to attach to for your current OS!"
            )

        path_to_core = args[0]

        return self._run_wrapper(log, path_to_core)

    def _run_wrapper(self, log, path_to_core):
        """
        Given the path to the core API, resolves the core path on all three OSes
        and then executes the unlocalize payload.

        :param log: Logger
        :param path_to_core: path to core root on current os.
        """

        # resolve the path to core on all platforms
        log.debug(
            "Running attach to core with specified path to core: '%s' " % path_to_core
        )
        core_locations = pipelineconfig_utils.resolve_all_os_paths_to_core(path_to_core)
        log.debug(
            "Resolved the following core path locations via install_location: %s"
            % core_locations
        )

        # and run the actual localize
        return _run_unlocalize(
            self.tk,
            log,
            core_locations["darwin"],
            core_locations["win32"],
            core_locations["linux2"],
            self._interaction_interface,
            copy_core=False,
        )


def _run_unlocalize(
    tk, log, mac_path, windows_path, linux_path, interaction_interface, copy_core
):
    """
    Actual execution payload for share_core and relocate_core. This method can be used to

    1. Share a core - e.g. copying it into a new location and then point the config
       to that location
    2. Attach to a core - e.g. discarding the current core and then point the config
       to another existing core.

    :param tk: API instance to operate on
    :param log: Logger
    :param mac_path: New core path on mac
    :param windows_path: New core path on windows
    :param linux_path: New core path on linux
    :param interaction_interface: Interface to use when interacting with the user.
    :param copy_core: Boolean. If true, the method will operate in "copy mode" where it tries
                      to copy the core out to an external location. If fase, it will instead
                      try to attach to an existing core.
    """

    log.debug("Executing the share_core command for %r" % tk)
    log.debug("Mac path: '%s'" % mac_path)
    log.debug("Windows path: '%s'" % windows_path)
    log.debug("Linux path: '%s'" % linux_path)
    log.debug("Current core version: %s" % tk.version)
    log.info("")

    # some basic checks first
    if not tk.pipeline_configuration.is_localized():
        raise TankError(
            "Looks like your current pipeline configuration is not localized and therefore "
            "does not contain its own copy of the Core API! This configuration is picking "
            "up its core from the following "
            "location: '%s'" % tk.pipeline_configuration.get_install_location()
        )

    # we need to have at least a path for the current os, otherwise we cannot introspect the API
    lookup = {"win32": windows_path, "linux2": linux_path, "darwin": mac_path}
    new_core_path_local = lookup[sgsix.platform]

    if not new_core_path_local:
        raise TankError(
            "You must specify a path to the core API for your current operating system."
        )

    if copy_core:
        # make sure location is empty
        if os.path.exists(new_core_path_local):
            raise TankError(
                "The path '%s' already exists on disk!" % new_core_path_local
            )

    else:
        # make sure location exists and that there is a recent enough API in there
        if not os.path.exists(new_core_path_local):
            raise TankError(
                "The path '%s' does not exist on disk!" % new_core_path_local
            )

        # ensure that the API we are switching to is as recent as the current
        new_core_version = pipelineconfig_utils.get_core_api_version(
            new_core_path_local
        )
        if is_version_older(new_core_version, tk.version):
            raise TankError(
                "You are currently running version %s of the core. It looks like the core "
                "in '%s' is version %s. You cannot switch to a version of the core that is "
                "older than the current core. Before switching, update the shared core and then "
                "try again!" % (tk.version, new_core_path_local, new_core_version)
            )

    pc_root = tk.pipeline_configuration.get_path()

    if copy_core:
        log.info(
            "This will move the embedded core API in the configuration '%s'." % pc_root
        )
        log.info("")

    log.info(
        "After this command has completed, the configuration will not contain an "
        "embedded copy of the core but instead it will be picked up from "
        "the following locations:"
    )
    log.info("")
    log.info(" - Linux: '%s'" % linux_path if linux_path else " - Linux: Not supported")
    log.info(
        " - Windows: '%s'" % windows_path
        if windows_path
        else " - Windows: Not supported"
    )
    log.info(" - Mac: '%s'" % mac_path if mac_path else " - Mac: Not supported")
    log.info("")
    log.info(
        "Note for expert users: Prior to executing this command, please ensure that you have "
        "no configurations that are using the core embedded in this configuration."
    )
    log.info("")

    # check with user if they wanna continue
    if not interaction_interface.ask_yn_question("Do you want to proceed"):
        # user pressed no
        log.info("Operation cancelled.")
        return

    # proceed with setup
    log.info("")

    old_umask = os.umask(0)
    try:

        # these core config files are directly related to the core
        # and not needed by a configuration
        core_config_file_names = [
            "shotgun.yml",
            "interpreter_Darwin.cfg",
            "interpreter_Linux.cfg",
            "interpreter_Windows.cfg",
        ]

        if copy_core:
            # first make the basic structure
            log.info("Setting up base structure...")
            os.mkdir(new_core_path_local, 0o775)

            # copy across the tank commands
            shutil.copy(
                os.path.join(pc_root, "tank"), os.path.join(new_core_path_local, "tank")
            )
            shutil.copy(
                os.path.join(pc_root, "tank.bat"),
                os.path.join(new_core_path_local, "tank.bat"),
            )

            # make the config folder
            log.info("Copying configuration files...")
            os.mkdir(os.path.join(new_core_path_local, "config"), 0o775)
            os.mkdir(os.path.join(new_core_path_local, "config", "core"), 0o775)

            for fn in core_config_file_names:
                log.debug("Copy %s..." % fn)
                shutil.copy(
                    os.path.join(pc_root, "config", "core", fn),
                    os.path.join(new_core_path_local, "config", "core", fn),
                )

            # create new install_location.yml file in the target location
            core_path = os.path.join(
                new_core_path_local, "config", "core", "install_location.yml"
            )
            fh = open(core_path, "wt")
            fh.write("# Tank configuration file\n")
            fh.write("# This file was automatically created\n")
            fh.write("\n")
            fh.write("# This file stores the location on disk where this\n")
            fh.write("# configuration is located. It is needed to ensure\n")
            fh.write("# that deployment works correctly on all os platforms.\n")
            fh.write(
                "Windows: '%s'\n" % windows_path
                if windows_path
                else "Windows: undefined_location\n"
            )
            fh.write(
                "Darwin: '%s'\n" % mac_path
                if mac_path
                else "Darwin: undefined_location\n"
            )
            fh.write(
                "Linux: '%s'\n" % linux_path
                if linux_path
                else "Linux: undefined_location\n"
            )
            fh.write("# End of file.\n")

            # copy the install
            log.info("Copying core installation...")
            filesystem.copy_folder(
                os.path.join(pc_root, "install"),
                os.path.join(new_core_path_local, "install"),
            )

        # back up current core API into the core.backup folder
        log.info("Backing up local core install...")
        current_core = os.path.join(pc_root, "install", "core")
        backup_folder_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_location = os.path.join(
            pc_root, "install", "core.backup", backup_folder_name
        )
        shutil.move(current_core, backup_location)

        # delete core system files
        log.info("Removing core system files from configuration...")
        for core_file in core_config_file_names:
            path = os.path.join(pc_root, "config", "core", core_file)
            try:
                log.debug("Removing system file '%s'" % path)
                os.chmod(path, 0o666)
                os.remove(path)
            except Exception as e:
                log.warning(
                    "Could not delete file '%s' - please delete by hand! "
                    "Error reported: %s" % (path, e)
                )

        # create blank core install
        log.info("Creating core proxy...")
        os.mkdir(current_core, 0o775)

        # copy python API proxy
        tank_proxy = os.path.join(
            new_core_path_local, "install", "core", "setup", "tank_api_proxy"
        )
        filesystem.copy_folder(
            tank_proxy, os.path.join(pc_root, "install", "core", "python")
        )

        # create core_XXX redirection files
        core_path = os.path.join(pc_root, "install", "core", "core_Darwin.cfg")
        fh = open(core_path, "wt")
        if mac_path:
            fh.write(mac_path)
        else:
            fh.write("undefined")
        fh.close()

        core_path = os.path.join(pc_root, "install", "core", "core_Linux.cfg")
        fh = open(core_path, "wt")
        if linux_path:
            fh.write(linux_path)
        else:
            fh.write("undefined")
        fh.close()

        core_path = os.path.join(pc_root, "install", "core", "core_Windows.cfg")
        fh = open(core_path, "wt")
        if windows_path:
            fh.write(windows_path)
        else:
            fh.write("undefined")
        fh.close()

    except Exception as e:
        raise TankError("Could not share the core! Error reported: %s" % e)
    finally:
        os.umask(old_umask)

    log.info("The Core API was successfully processed.")
    log.info("")
