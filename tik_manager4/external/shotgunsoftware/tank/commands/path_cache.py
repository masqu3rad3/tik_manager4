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
Methods relating to the path cache
"""

from ..errors import TankError
from .. import path_cache
from .. import folder

from .action_base import Action
from tank_vendor.six.moves import input


class SynchronizePathCache(Action):
    """
    Tank command to synchronize the local disk path cache
    with the FilesystemLocation entity on disk.
    """

    def __init__(self):
        """
        Constructor
        """
        Action.__init__(
            self,
            "synchronize_folders",
            Action.TK_INSTANCE,
            (
                "Ensures that the local folders and folder metadata is up to date with Flow Production Tracking."
            ),
            "Admin",
        )

        # this method can be executed via the API
        self.supports_api = True
        self.parameters = {}
        self.parameters["full_sync"] = {
            "description": "Perform a full sync",
            "default": False,
            "type": "bool",
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
        return self._run(log, computed_params["full_sync"])

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        if len(args) == 1 and args[0] == "--full":
            full_sync = True

        elif len(args) == 0:
            full_sync = False

        else:
            raise TankError("Syntax: synchronize_folders [--full]")

        return self._run(log, full_sync)

    def _run(self, log, full_sync):
        """
        Actual business logic for command

        :param log: logger
        :param full_sync: boolean flag to indicate that a full sync should be carried out
        """

        if self.tk.pipeline_configuration.get_shotgun_path_cache_enabled():

            log.info("Ensuring that the local folder representation is up to date...")

            if full_sync:
                log.info("Doing a full sync.")
            else:
                log.info(
                    "Will try to do an incremental sync. If you want to force a complete re-sync, "
                    "run this command with a --full flag."
                )

            folder.synchronize_folders(self.tk, full_sync)

            log.info("Local folder information has been synchronized.")

        else:
            # remote cache not turned on for this project
            log.error(
                "Looks like this project doesn't synchronize its folders with Flow Production Tracking! "
                "If you want to turn on synchronization for this project, run "
                "the 'upgrade_folders' tank command."
            )


class PathCacheMigrationAction(Action):
    """
    Tank command for migrating an existing project to use the new FilesystemLocation
    based syncing. After the migration command has been executed, the project will get
    its shotgun path cache flag enabled and an initial sync is carried out.
    """

    def __init__(self):
        """
        Constructor
        """
        Action.__init__(
            self,
            "upgrade_folders",
            Action.TK_INSTANCE,
            (
                "Upgrades on old project to use the shared folder "
                "generation that was introduced in Toolkit 0.15"
            ),
            "Admin",
        )

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """

        log.info("Welcome to the folder sync upgrade command!")
        log.info("")
        log.info(
            "Projects created with Toolkit v0.14 and earlier do not automatically synchronize "
            "their folders on disk with Flow Production Tracking. You can use this command to turn on that folder "
            "sync."
        )
        log.info("")

        if self.tk.pipeline_configuration.get_shotgun_path_cache_enabled():
            log.info("Looks like syncing is already turned on! Nothing to do!")
            return

        log.info(
            "Turning on folder sync will first do a full synchronization of the "
            "existing folders. After that, syncing will happen incrementally in the "
            "background."
        )
        log.info("")
        log.info(
            "Note! If you have any cloned pipeline configurations for this project, you must run "
            "'tank upgrade_folders' for each one of them in order for them to pick up folders "
            "from Flow Production Tracking."
        )
        log.info("")
        val = input(
            "Turn on syncing for this pipeline configuration (Yes/No) ? [Yes]: "
        )
        if val != "" and not val.lower().startswith("y"):
            log.info("Exiting! Syncing will not be turned on.")
            return

        # first load up the current path cache file and make sure
        # shotgun has got all those entries present as FilesystemLocations.
        log.info("")
        log.info("Phase 1/3: Pushing data from the current path cache to Flow Production Tracking...")
        curr_pc = path_cache.PathCache(self.tk)
        try:
            curr_pc.ensure_all_entries_are_in_shotgun()
        finally:
            curr_pc.close()

        # now turn on the cloud based path cache. This means that from now on, a new path
        # cache, stored on the local disk, will be used instead of the previous (shared) one.
        log.info("")
        log.info("Phase 2/3: Switching on the PTR Path Cache...")
        self.tk.pipeline_configuration.turn_on_shotgun_path_cache()

        # and synchronize path cache
        log.info("")
        log.info("Phase 3/3: Synchronizing your local machine with Flow Production Tracking...")
        pc = path_cache.PathCache(self.tk)
        try:
            pc.synchronize(full_sync=True)
        finally:
            pc.close()

        log.info("")
        log.info(
            "All done! This project and pipeline configuration is now synchronizing its folders with Flow Production Tracking."
        )
        log.info("")
        log.info(
            "Once all pipeline configurations for this project have been upgraded, the previous path cache "
            "file, located in PROJECT_ROOT/tank/cache, is no longer needed and can be removed."
        )
        log.info("")
        log.info("")
