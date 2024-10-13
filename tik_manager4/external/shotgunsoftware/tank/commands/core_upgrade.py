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
Tank command allowing to do core updates.
"""

from __future__ import with_statement

from ..errors import TankError
from .action_base import Action

import os
import sys
import textwrap
import optparse
import copy

from ..util import shotgun
from .. import pipelineconfig_utils
from . import console_utils
from ..util.version import is_version_newer, is_version_head

from tank_vendor import yaml


# FIXME: This should be refactored into something that can be used by other commands.
class TkOptParse(optparse.OptionParser):
    """
    Toolkit option parser for tank commands. It makes the interface and messages compatible with how Toolkit
    displays errors.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        # Don't generate the --help options, since --help is already eaten up by tank_cmd.py
        kwargs = copy.copy(kwargs)
        kwargs["add_help_option"] = False
        optparse.OptionParser.__init__(self, *args, **kwargs)
        # optparse uses argv[0] for the program, but users use the tank command instead, so replace
        # the program.
        self.prog = "tank"

    def error(self, msg):
        """
        :param msg: Error message for the TankError.

        :raises TankError: Throws a TankError with the message passed in.
        """
        raise TankError(msg)


class CoreUpdateAction(Action):
    """
    Action to update the Core API code that is associated with the currently running code.
    """

    def __init__(self):
        """
        Constructor.
        """
        Action.__init__(
            self,
            "core",
            Action.GLOBAL,
            "Updates your Toolkit Core API to a different version.",
            "Configuration",
        )

        # this method can be executed via the API
        self.supports_api = True

        ret_val_doc = "Returns a dictionary with keys status (str) optional keys. The following status codes "
        ret_val_doc += "are returned: 'up_to_date' if no update was needed, 'updated' if an update was "
        ret_val_doc += "applied and 'update_blocked' if an update was available but could not be applied. "
        ret_val_doc += "For the 'updated' status, data will contain new_version key with the version "
        ret_val_doc += "number of the core that was updated to. "
        ret_val_doc += "For the 'update_blocked' status, data will contain a reason key containing an explanation."

        self.parameters = {"return_value": {"description": ret_val_doc, "type": "dict"}}

    def _parse_arguments(self, parameters):
        """
        Parses the list of arguments from the command line.

        :param parameters: The content of argv that hasn't been processed by the tank command.

        :returns: The core version. None if --version wasn't specified.
        """
        parser = TkOptParse()
        parser.set_usage(optparse.SUPPRESS_USAGE)
        parser.add_option("-v", "--version", type="string", default=None)
        options, args = parser.parse_args(parameters)

        if options.version is not None and not options.version.startswith("v"):
            parser.error("version string should always start with 'v'")
        return options.version

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        return self._run(log, parameters[0] if len(parameters) else None)

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        core_version = self._parse_arguments(args)

        self._run(log, core_version)

    def _run(self, log, core_version):
        """
        Actual execution payload.

        :param log: std python logger
        :param core_version: Version to update the core to. If None, updates the core to the latest version.
        """
        return_status = {"status": "unknown"}

        # get the core api root of this installation by looking at the relative location of the running code.
        code_install_root = pipelineconfig_utils.get_path_to_current_core()

        log.info("")
        log.info("Welcome to the Flow Production Tracking Toolkit update checker!")
        log.info("This script will check if the Toolkit Core API installed")
        log.info("in %s" % code_install_root)
        log.info("is up to date.")
        log.info("")
        log.info("")

        log.info(
            "Please note that if this is a shared Toolkit Core used by more than one project, "
            "this will affect all of the projects that use it. If you want to test a Core API "
            "update in isolation, prior to rolling it out to multiple projects, we recommend "
            "creating a special *localized* pipeline configuration."
        )
        log.info("")
        log.info("For more information, please see the Toolkit documentation:")
        log.info(
            "https://help.autodesk.com/view/SGDEV/ENU/?contextId=PC_FRAMEWORK_DESKTOPSTARTUP"
        )
        log.info(
            "https://help.autodesk.com/view/SGDEV/ENU/?contextId=PC_TOOLKIT_FRAMEWORKS"
        )
        log.info("")

        config_desc = self.tk.configuration_descriptor if self.tk is not None else None

        installer = TankCoreUpdater(code_install_root, log, core_version, config_desc)
        current_version = installer.get_current_version_number()
        new_version = installer.get_update_version_number()
        log.info(
            "You are currently running version %s of the Flow Production Tracking Toolkit"
            % current_version
        )

        status = installer.get_update_status()

        if status == TankCoreUpdater.UP_TO_DATE:
            log.info("No need to update the Toolkit Core API at this time!")
            return_status = {"status": "up_to_date"}

        elif status == TankCoreUpdater.UPDATE_BLOCKED_BY_SG:
            req_sg = installer.get_required_sg_version_for_update()
            msg = (
                "%s version of core requires a more recent version (%s) of Flow Production Tracking!"
                % ("The newest" if core_version is None else "The requested", req_sg)
            )
            log.error(msg)
            return_status = {"status": "update_blocked", "reason": msg}

        elif status == TankCoreUpdater.UPDATE_BLOCKED_BY_CONFIG:
            # The config is immutable so can't be updated.
            descriptor_type = config_desc.get_dict().get("type", "type unknown.")
            msg = (
                "The core on this config can't be updated using this method,"
                ' as the config is using a "%s" type descriptor.'
                " Please update the source configuration." % descriptor_type
            )
            log.error(msg)
            return_status = {"status": "update_blocked", "reason": msg}

        elif status == TankCoreUpdater.UPDATE_POSSIBLE:

            (summary, url) = installer.get_release_notes()

            log.info("")
            log.info("Newer version %s is available." % new_version)
            log.info("")
            log.info("Change Summary:")
            for x in textwrap.wrap(summary, width=60):
                log.info(x)
            log.info("")
            log.info("Detailed Release Notes:")
            log.info("%s" % url)
            log.info("")
            log.info(
                "Please note that if this is a shared core used by more than one project, "
                "this will affect the other projects as well."
            )
            log.info("")

            if self._interaction_interface.ask_yn_question(
                "Update to %s of the Core API?" % new_version
            ):
                # install it!
                installer.do_install()

                log.info("")
                log.info("")
                log.info(
                    "----------------------------------------------------------------"
                )
                log.info("The Toolkit Core API has been updated!")
                log.info("")
                log.info("")
                log.info("Please note the following:")
                log.info("")
                log.info(
                    "- You need to restart any applications (such as Maya or Nuke)"
                )
                log.info("  in order for them to pick up the API update.")
                log.info("")
                log.info("- Please close this shell, as the update process")
                log.info("  has replaced the folder that this script resides in")
                log.info("  with a more recent version. ")
                log.info("")
                log.info(
                    "----------------------------------------------------------------"
                )
                log.info("")
                return_status = {"status": "updated", "new_version": new_version}

            else:
                log.info("The Flow Production Tracking Toolkit will not be updated.")

        else:
            raise TankError("Unknown Update state!")

        return return_status


class TankCoreUpdater(object):
    """
    Class which handles the update of the core API.
    """

    # possible update status states
    (
        UP_TO_DATE,  # all good, no update necessary
        UPDATE_POSSIBLE,  # more recent version exists
        UPDATE_BLOCKED_BY_SG,  # more recent version exists but PTR version is too low.
        UPDATE_BLOCKED_BY_CONFIG,  # The config descriptor is not suitable for updating.
    ) = range(4)

    def __init__(
        self, install_folder_root, logger, core_version=None, config_desc=None
    ):
        """
        Constructor

        :param install_folder_root: The path to the installation to check. This is either a localized
                                   Pipeline Configuration or a studio code location (omit the install folder).
                                   Because we are passing this parameter in explicitly, the currently running
                                   code base does not have to be related to the code base that is being updated,
                                   e.g. you can run the updater as a totally separate thing.
        :param logger: Logger to send output to.
        :param core_version: Version of the core to update to. If None, the core will be updated to the latest
                             version. Defaults to None.
        """
        self._log = logger
        self._configuration_descriptor = config_desc

        from ..descriptor import Descriptor, create_descriptor

        self._local_sg = shotgun.get_sg_connection()

        if not core_version:
            uri = "sgtk:descriptor:app_store?name=tk-core"
            self._new_core_descriptor = create_descriptor(
                self._local_sg, Descriptor.CORE, uri, resolve_latest=True
            )
        else:
            uri = "sgtk:descriptor:app_store?name=tk-core&version=%s" % core_version
            self._new_core_descriptor = create_descriptor(
                self._local_sg, Descriptor.CORE, uri
            )

        self._install_root = os.path.join(install_folder_root, "install")

        # now also extract the version of shotgun currently running
        try:
            self._sg_studio_version = ".".join(
                [str(x) for x in self._local_sg.server_info["version"]]
            )
        except Exception as e:
            raise TankError("Could not extract version number for shotgun: %s" % e)

    def get_update_version_number(self):
        """
        Returns the new version of the Toolkit API from shotgun
        Returns None if there is no new version
        """
        return self._new_core_descriptor.version

    def get_current_version_number(self):
        """
        Returns the currently installed version of the Toolkit API
        """
        return pipelineconfig_utils.get_currently_running_api_version()

    def get_required_sg_version_for_update(self):
        """
        Returns the PTR version that is required in order to update to the specified
        version of the Tank Core API.

        :returns: sg version number as a string or None if no version is required.
        """
        return self._new_core_descriptor.version_constraints["min_sg"]

    def get_release_notes(self):
        """
        Returns the release notes for the most recent version of the Toolkit API

        :returns: tuple with (summary_string, details_url_string)
        """
        return self._new_core_descriptor.changelog

    def get_update_status(self):
        """
        Returns true if an update is recommended. As a side effect, if pulls down
        the core from the AppStore to get access to the info.yml file so we can
        get the required Shotgun version.
        """
        if is_version_head(self.get_current_version_number()):
            # head is the version number which is stored in tank core trunk
            # getting this as a result means that we are not actually running
            # a version of tank that came from the app store, but some sort
            # of dev version
            return self.UP_TO_DATE

        elif self.get_current_version_number() == self._new_core_descriptor.version:
            # running updated version already
            return self.UP_TO_DATE
        elif (
            self._configuration_descriptor
            and self._configuration_descriptor.is_immutable()
        ):
            # The config is immutable so we should not try updating it.
            return TankCoreUpdater.UPDATE_BLOCKED_BY_CONFIG
        else:

            # FIXME: We should cache info.yml on the appstore so we don't have
            #  to download the whole bundle just to see the file.
            if not self._new_core_descriptor.exists_local():
                self._log.info("")
                self._log.info(
                    "Downloading Toolkit Core API %s from the App Store..."
                    % self._new_core_descriptor.version
                )
                self._new_core_descriptor.download_local()
                self._log.info("Download completed.")

            # running an older version. Make sure that shotgun has the required version
            req_sg = self.get_required_sg_version_for_update()
            if req_sg is None:
                # no particular version required! We are good to go!
                return TankCoreUpdater.UPDATE_POSSIBLE
            else:
                # there is a sg min version required - make sure we have that!
                if is_version_newer(req_sg, self._sg_studio_version):
                    return TankCoreUpdater.UPDATE_BLOCKED_BY_SG
                else:
                    return TankCoreUpdater.UPDATE_POSSIBLE

    def do_install(self):
        """
        Installs the requested core and updates core_api.yml.
        """

        # We should check to see if the config is using a dev descriptor
        # because if we are we don't want to update the cached version of the config,
        # instead we want to update the core_api.yml in the dev config location.
        if self._configuration_descriptor and self._configuration_descriptor.is_dev():
            # We shouldn't try to install the core, a reload will be required to re cache things,
            # just update the core_api.yml instead.
            root = self._configuration_descriptor.get_path()
            self._update_core_api_descriptor(root)

        else:
            self._install_core()
            root = os.path.join(os.path.dirname(self._install_root), "config")
            self._update_core_api_descriptor(root)

    def _install_core(self):
        """
        Performs the actual installation of the new version of the core API
        """
        self._log.info("Now installing Toolkit Core.")

        sys.path.insert(0, self._new_core_descriptor.get_path())
        try:
            import _core_upgrader

            _core_upgrader.upgrade_tank(self._install_root, self._log)
        except Exception as e:
            self._log.exception(e)
            raise Exception("Could not run update script! Error reported: %s" % e)

    def _update_core_api_descriptor(self, config_root):
        """
        Updates the core_api.yml descriptor file.
        """

        core_api_yaml_path = os.path.join(config_root, "core", "core_api.yml")

        message = (
            "# Flow Production Tracking Toolkit configuration file. This file was automatically\n"
            "# created during the latest core update.\n"
        )
        with open(core_api_yaml_path, "w") as f:
            f.writelines(message)
            yaml.safe_dump(
                {"location": self._new_core_descriptor.get_dict()},
                f,
                default_flow_style=False,
            )
