# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .. import folder
from ..errors import TankError
from .action_base import Action


class CreateFoldersAction(Action):
    """
    Action for creating folders on disk
    """

    def __init__(self):
        Action.__init__(
            self,
            "folders",
            Action.CTX,
            (
                "Creates folders on disk for your current context. This command is "
                "typically used in conjunction with a PTR entity, for example "
                "'tank Shot P01 folders' in order to create folders on disk for Shot P01."
            ),
            "Production",
        )

    def run_interactive(self, log, args):
        if len(args) != 0:
            raise TankError("This command takes no arguments!")

        if self.context.project is None:
            log.info("Looks like your context is empty! No folders to create!")
            return

        # first do project
        entity_type = self.context.project["type"]
        entity_id = self.context.project["id"]
        # if there is an entity then that takes precedence
        if self.context.entity:
            entity_type = self.context.entity["type"]
            entity_id = self.context.entity["id"]
        # and if there is a task that is even better
        if self.context.task:
            entity_type = self.context.task["type"]
            entity_id = self.context.task["id"]

        log.info("Creating folders, stand by...")
        f = folder.process_filesystem_structure(
            self.tk, entity_type, entity_id, False, None
        )
        log.info("")
        log.info("The following items were processed:")
        for x in f:
            log.info(" - %s" % x)
        log.info("")
        log.info("In total, %s folders were processed." % len(f))
        log.info("")


class PreviewFoldersAction(Action):
    """
    Action for doing a folder creation preview
    """

    def __init__(self):
        Action.__init__(
            self,
            "preview_folders",
            Action.CTX,
            (
                "Previews folders on disk for your current context. This command is "
                "typically used in conjunction with a PTR entity, for example "
                "'tank Shot P01 preview_folders' in order to show what folders "
                "would be created if you ran the folders command for Shot P01."
            ),
            "Production",
        )

    def run_interactive(self, log, args):
        if len(args) != 0:
            raise TankError("This command takes no arguments!")

        if self.context.project is None:
            log.info("Looks like your context is empty! No folders to preview!")
            return

        # first do project
        entity_type = self.context.project["type"]
        entity_id = self.context.project["id"]
        # if there is an entity then that takes precedence
        if self.context.entity:
            entity_type = self.context.entity["type"]
            entity_id = self.context.entity["id"]
        # and if there is a task that is even better
        if self.context.task:
            entity_type = self.context.task["type"]
            entity_id = self.context.task["id"]

        log.info("Previewing folder creation, stand by...")
        f = folder.process_filesystem_structure(
            self.tk, entity_type, entity_id, True, None
        )
        log.info("")
        log.info("The following items were processed:")
        for x in f:
            log.info(" - %s" % x)
        log.info("")
        log.info("In total, %s folders were processed." % len(f))
        log.info("Note - this was a preview and no actual folders were created.")
