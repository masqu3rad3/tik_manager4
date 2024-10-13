# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from .. import pipelineconfig_utils
from ..util import ShotgunPath
from . import constants
from ..errors import TankError
from .action_base import Action

import os


class PCBreakdownAction(Action):
    """
    Action that shows an overview of all the pipeline configurations for a project
    """

    def __init__(self):
        Action.__init__(
            self,
            "configurations",
            Action.TK_INSTANCE,
            (
                "Shows an overview of the different configurations registered with this project."
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
        return self._run(log)

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        if len(args) != 0:
            raise TankError("This command takes no arguments!")
        return self._run(log)

    def _run(self, log):
        """
        Actual execution payload
        """

        log.info("Fetching data from Flow Production Tracking...")
        log.info("")
        log.info("")
        log.info("=" * 70)
        if self.tk.pipeline_configuration.is_site_configuration():
            log.info("Available Configurations for Site")
            sg_project_link = None
        else:
            project_id = self.tk.pipeline_configuration.get_project_id()
            proj_data = self.tk.shotgun.find_one(
                "Project", [["id", "is", project_id]], ["name"]
            )
            log.info(
                "Available Configurations for Project '%s'" % proj_data.get("name")
            )
            sg_project_link = {"type": "Project", "id": project_id}

        log.info("=" * 70)
        log.info("")

        data = self.tk.shotgun.find(
            constants.PIPELINE_CONFIGURATION_ENTITY,
            [["project", "is", sg_project_link]],
            ["code", "users", "mac_path", "windows_path", "linux_path"],
        )
        for d in data:

            if len(d.get("users")) == 0:
                log.info("Configuration '%s' (Public)" % d.get("code"))
            else:
                log.info("Configuration '%s' (Private)" % d.get("code"))

            log.info("-------------------------------------------------------")
            log.info("")

            if d.get("code") == constants.PRIMARY_PIPELINE_CONFIG_NAME:
                log.info(
                    "This is the Project Master Configuration. It will be used whenever "
                    "this project is accessed from a studio level tank command or API "
                    "constructor."
                )

            log.info("")
            lp = d.get("linux_path")
            mp = d.get("mac_path")
            wp = d.get("windows_path")
            if lp is None:
                lp = "[Not defined]"
            if wp is None:
                wp = "[Not defined]"
            if mp is None:
                mp = "[Not defined]"

            log.info("Linux Location:   %s" % lp)
            log.info("Windows Location: %s" % wp)
            log.info("Mac Location:     %s" % mp)
            log.info("")

            # check for core API etc.
            if self.tk.pipeline_configuration.is_auto_path():
                local_path = self.tk.pipeline_configuration.get_path()
            else:
                local_path = d.get(ShotgunPath.get_shotgun_storage_key())

            if local_path is None:
                log.info("The Configuration is not accessible from this computer!")

            elif not os.path.exists(local_path):
                log.info("The Configuration cannot be found on disk!")

            else:
                # yay, exists on disk
                local_tank_command = os.path.join(local_path, "tank")

                if pipelineconfig_utils.is_localized(local_path):
                    log.info(
                        "This configuration is running its own version of the Toolkit API."
                    )
                    log.info("If you want to check for core API updates you can run:")
                    log.info("> %s core" % local_tank_command)
                    log.info("")

                else:

                    log.info(
                        "This configuration is using a shared version of the Toolkit API."
                        "If you want it to run its own independent version "
                        "of the Toolkit Core API, you can run:"
                    )
                    log.info("> %s localize" % local_tank_command)
                    log.info("")

                log.info("If you want to check for app or engine updates, you can run:")
                log.info("> %s updates" % local_tank_command)
                log.info("")

                log.info(
                    "If you want to change the location of this configuration, you can run:"
                )
                log.info("> %s move_configuration" % local_tank_command)
                log.info("")

            if len(d.get("users")) == 0:
                log.info(
                    "This is a public configuration. In Flow Production Tracking, the actions defined in this "
                    "configuration will be on all users' menus."
                )

            elif len(d.get("users")) == 1:
                log.info(
                    "This is a private configuration. In Flow Production Tracking, only %s will see the actions "
                    "defined in this config. If you want to add additional members to this "
                    "configuration, navigate to the PTR Pipeline Configuration Page "
                    "and add them to the Users field." % d.get("users")[0]["name"]
                )

            elif len(d.get("users")) > 1:
                users = ", ".join([u.get("name") for u in d.get("users")])
                log.info(
                    "This is a private configuration. In Flow Production Tracking, the following users will see "
                    "the actions defined in this config: %s. If you want to add additional "
                    "members to this configuration, navigate to the PTR Pipeline "
                    "Configuration Page and add them to the Users field." % users
                )

            log.info("")
            log.info("")
