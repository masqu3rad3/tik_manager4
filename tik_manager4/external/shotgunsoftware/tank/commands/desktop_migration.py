# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .action_base import Action
from . import console_utils
from . import constants

_MESSAGE = (
    "This command will migrate the PTR site configuration used by the Desktop app so "
    "it is no longer associated with the 'Template Project'. Before proceeding, make sure "
    "all your users are running version 1.2.0 or greater of the PTR desktop app Startup "
    "framework. You can see which version you are running in the PTR desktop app's About "
    "Box. If you don't see the Startup version mentionned in the About Box, you must "
    "install the latest release of the PTR desktop app.\n"
    "WARNING: If there are people using older versions of the PTR desktop app with your "
    "site, they will get an error when starting Desktop after the migration.."
)


class DesktopMigration(Action):
    """
    Action that migrates the Flow Production Tracking away from the Template Project.
    """

    def __init__(self):
        """
        Constructor
        """
        Action.__init__(
            self,
            "migrate_desktop",
            Action.TK_INSTANCE,
            "Migrates PTR desktop app away from the Template Project.",
            "Admin",
        )

    def run_interactive(self, log, args):
        """
        Tank command accessor (tank migrate_desktop)
        Retrieves the pipeline configuration from Shotgun
        and unassigns it from the Template Project.

        :param log: std python logger
        :param args: command line args
        """
        log.info("Retrieving pipeline configuration from Flow Production Tracking...")
        log.info("")

        pc = self.tk.pipeline_configuration

        if pc.is_unmanaged():
            log.error(
                "Cannot migrate a setup which does not have a pipeline configuration in Flow Production Tracking!"
            )
            return

        # Fetch the project id from the actual pipeline configuration.
        sg_pc = self.tk.shotgun.find_one(
            constants.PIPELINE_CONFIGURATION_ENTITY,
            [["id", "is", pc.get_shotgun_id()]],
            ["id", "code", "project"],
        )

        # If the pipeline configuration doesn't exist anymore, abort.
        if not sg_pc:
            log.error(
                "Pipeline configuration '%d' doesn't seem to exist anymore."
                % pc.get_shotgun_id()
            )
            return

        # If a pipeline configuration is not assigned to the Template Project, abort.
        if (
            sg_pc["project"] is not None
            and sg_pc["project"]["name"] != "Template Project"
        ):
            log.error(
                'This migration only supports configurations linked to "Template Project". '
                'The current configuration (named "%s" with id %d) is linked to the project '
                '"%s" with id %d.'
                % (
                    sg_pc["code"],
                    sg_pc["id"],
                    sg_pc["project"]["name"],
                    sg_pc["project"]["id"],
                )
            )
            return

        log.info(_MESSAGE)

        # Make sure the user really wants to go forward with the migration.
        do_migration = self._interaction_interface.ask_yn_question(
            "Do you want to continue?"
        )

        if not do_migration:
            log.info("Migration aborted.")
            return

        if sg_pc["project"]:
            # Allright, we can now update the pipeline configuration to make it projectless.
            self.tk.shotgun.update(
                constants.PIPELINE_CONFIGURATION_ENTITY,
                pc.get_shotgun_id(),
                {"project": None},
            )
            log.debug("Pipeline configuration updated in Flow Production Tracking.")
        else:
            log.warning(
                "Pipeline configuration isn't assigned to a project in Flow Production Tracking."
            )

        # Upgrade site configuration on disk.
        if not pc.is_site_configuration():
            pc.convert_to_site_config()
            log.debug("Site Configuration updated.")
        else:
            log.warning("Site configuration is already updated.")

        log.info("The migration completed successfully.")
