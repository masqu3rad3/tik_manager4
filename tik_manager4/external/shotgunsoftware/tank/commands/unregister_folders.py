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
Method to unregister folders from the path cache
"""

from ..errors import TankError
from .. import path_cache
from .action_base import Action
from ..util.login import get_current_user
from tank_vendor.six.moves import input, zip


class UnregisterFoldersAction(Action):
    """
    Tank command for unregistering a folder on disk from Shotgun. This is part of the process of
    the deletion of a folder on disk. As part of removing or moving, the folder needs to be
    unregistered with Shotgun to ensure that the connection between that path and the related
    entity is undone.
    """

    def __init__(self):
        """
        Constructor
        """
        Action.__init__(
            self,
            "unregister_folders",
            Action.TK_INSTANCE,
            ("Unregisters the folders for an object in Flow Production Tracking."),
            "Admin",
        )

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        self.parameters["path"] = {
            "description": "Path to unregister. Any child paths will be unregistered too.",
            "default": None,
            "type": "str",
        }

        self.parameters["entity"] = {
            "description": (
                "Entity to unregister. Should be a Flow Production Tracking-style entity "
                "dictionary with keys 'type' and 'id'."
            ),
            "default": None,
            "type": "dict",
        }

        self.parameters["return_value"] = {
            "description": (
                "List of dictionaries where each dict contains "
                "the path and entity data for an unregistered path"
            ),
            "type": "list",
        }

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: Std logging object
        :param parameters: Std tank command parameters dict
        """

        if self.tk.pipeline_configuration.is_site_configuration():
            log.error("This command is not supported with the site configuration.")
            return

        if not self.tk.pipeline_configuration.get_shotgun_path_cache_enabled():
            # remote cache not turned on for this project
            log.error(
                "Looks like this project doesn't synchronize its folders with Flow Production Tracking! "
                "If you'd like to upgrade your path cache to turn on synchronization for "
                "this project, run the 'tank upgrade_folders' command."
            )
            return

        # there are multiple syntaxes for this command
        # - context based: tank Shot ABC123 unregister_folders
        # - path based: tank unregister_folders path1, path2, path3

        if self.context.task:
            # task based - e.g. 'tank Task @12345 unregister_folders'
            self._unregister_entity(self.context.task, log, prompt=True)

        elif self.context.entity:
            # context based - e.g. 'tank Shot ABC123 unregister_folders'
            self._unregister_entity(self.context.entity, log, prompt=True)

        else:
            # no context - so it is path based instead
            if len(args) == 0:
                # display help message

                log.info(
                    "Unregister folders on your filesystem that are being tracked by Toolkit. "
                    "When applications are launched and folders are created on your filesystem, "
                    "new entries are stored in PTR as FilesystemLocation entities. These "
                    "records are called the 'path cache', and are used to track the relationship "
                    "between PTR entities and folders on disk. Use this command if you ever "
                    "need to remove these associations."
                )
                log.info("")
                log.info("You can unregister all folders for a project:")
                log.info("> tank unregister_folders --all")
                log.info("")
                log.info("You can unregister all folders matching a certain pattern:")
                log.info("> tank unregister_folders --filter='john.smith'")
                log.info("")
                log.info("Pass in a PTR entity (by name or id):")
                log.info("> tank Shot ABC123 unregister_folders")
                log.info("")
                log.info("Or pass in one or more paths:")
                log.info(
                    "> tank unregister_folders /path/to/folder_a /path/to/folder_b ..."
                )
                log.info("")

            elif len(args) == 1 and args[0] == "--all":

                if self.context.project is None:
                    log.error("You need to specify a project for the --all parameter.")
                    return []

                log.info("This will unregister all folders for the project.")
                self._unregister_entity(self.context.project, log, prompt=True)

            elif len(args) == 1 and args[0].startswith("--filter="):

                # from '--filter=john.smith' get 'john.smith'
                filter_str = args[0][len("--filter=") :]

                if filter_str == "":
                    log.error("You need to specify a filter!")
                    return []

                if self.context.project is None:
                    log.error("You need to specify a project!")
                    return []

                log.info(
                    "This will unregister all folders containing the string '%s'."
                    % filter_str
                )

                # get the filesystem location ids which are associated with the entity
                sg_data = self.tk.shotgun.find(
                    path_cache.SHOTGUN_ENTITY,
                    [
                        ["project", "is", self.context.project],
                        ["code", "contains", filter_str],
                    ],
                )
                sg_ids = [x["id"] for x in sg_data]
                log.debug(
                    "The following path cache ids are linked to the entity: %s" % sg_ids
                )
                self._unregister_filesystem_location_ids(sg_ids, log, prompt=True)

            else:
                paths = args
                log.info("Unregistering the following folders:")
                for p in paths:
                    log.info(" - %s" % p)
                log.info("")
                self._unregister_paths(paths, log, prompt=True)

    def run_noninteractive(self, log, parameters):
        """
        API accessor

        :param log: Std logging object
        :param parameters: Std tank command parameters dict
        :returns: List of dictionaries to represents the items that were unregistered.
                  Each dictionary has keys path and entity, where entity is a standard
                  Shotgun-style link dictionary containing the keys type and id.
                  Note that the shotgun ids returned will refer to retired objects in
                  Shotgun rather than live ones.
        """

        if self.tk.pipeline_configuration.is_site_configuration():
            log.error("This command is not supported with the site configuration.")
            return
        # validate params and seed default values
        computed_params = self._validate_parameters(parameters)

        # must have a path or an entity
        if computed_params["path"] is None and computed_params["entity"] is None:
            raise TankError("Must either specify a path or an entity!")
        # ... but not both
        if computed_params["path"] and computed_params["entity"]:
            raise TankError("Cannot specify both a path and an entity!")

        if computed_params["path"]:
            path = computed_params["path"]
            return self._unregister_paths([path], log, prompt=False)

        if computed_params["entity"]:
            entity = computed_params["entity"]
            if "id" not in entity:
                raise TankError("Entity dictionary does not contain an id key!")
            if "type" not in entity:
                raise TankError("Entity dictionary does not contain a type key!")
            return self._unregister_entity(entity, log, prompt=False)

    def _unregister_paths(self, paths, log, prompt):
        """
        Unregisters a path.

        :param paths: list of paths to unregister
        :param log: python logger
        :param prompt: Boolean to indicate that we can prompt the user for information or confirmation
        :returns: List of dictionaries to represents the items that were unregistered.
                  Each dictionary has keys path and entity, where entity is a standard
                  Shotgun-style link dictionary containing the keys type and id.
                  Note that the shotgun ids returned will refer to retired objects in
                  Shotgun rather than live ones.
        """
        log.debug("Will unregister folders for the following root paths:")
        for p in paths:
            log.debug(p)

        pc = path_cache.PathCache(self.tk)
        try:

            # first of all, make sure we are up to date
            pc.synchronize()

            # now get a unique list of filesystemlocation ids for the paths
            fs_location_ids = set()
            for p in paths:
                sg_id = pc.get_shotgun_id_from_path(p)
                if sg_id is None:
                    log.warning("Path '%s' is not registered in PTR - ignoring." % p)
                else:
                    log.debug(
                        "The path '%s' matches FilesystemLocation id: %s" % (p, sg_id)
                    )
                    fs_location_ids.add(sg_id)

        finally:
            pc.close()

        return self._unregister_filesystem_location_ids(
            list(fs_location_ids), log, prompt
        )

    def _unregister_entity(self, entity, log, prompt):
        """
        Unregisters an entity from the path cache in Shotgun.

        :param entity: Shotgun entity dict (e.g Shot, Asset or Task) with keys type and id
        :param log: Logger
        :param prompt: If true, the command may prompt the user for confirmation
        :returns: List of dictionaries to represents the items that were unregistered.
                  Each dictionary has keys path and entity, where entity is a standard
                  Shotgun-style link dictionary containing the keys type and id.
                  Note that the shotgun ids returned will refer to retired objects in
                  Shotgun rather than live ones.
        """
        log.debug("Unregister folders for PTR Entity %s..." % entity)

        # get the filesystem location ids which are associated with the entity
        sg_data = self.tk.shotgun.find(
            path_cache.SHOTGUN_ENTITY, [[path_cache.SG_ENTITY_FIELD, "is", entity]]
        )
        sg_ids = [x["id"] for x in sg_data]
        log.debug("The following path cache ids are linked to the entity: %s" % sg_ids)
        return self._unregister_filesystem_location_ids(sg_ids, log, prompt)

    def _unregister_filesystem_location_ids(self, ids, log, prompt):
        """
        Performs the unregistration of a path from the path cache database.
        Will recursively unregister any child items parented to the given
        filesystem location id.

        :param ids: List of filesystem location ids to unregister
        :param log: Logging instance
        :param prompt: Should the user be presented with confirmation prompts?
        :returns: List of dictionaries to represents the items that were unregistered.
                  Each dictionary has keys path and entity, where entity is a standard
                  Shotgun-style link dictionary containing the keys type and id.
                  Note that the shotgun ids returned will refer to retired objects in
                  Shotgun rather than live ones.
        """
        # tuple index constants for readability

        if len(ids) == 0:
            log.info("No associated folders found!")
            return []

        # first of all, make sure we are up to date.
        pc = path_cache.PathCache(self.tk)
        try:
            pc.synchronize()
        finally:
            pc.close()

        # now use the path cache to get a list of all folders (recursively) that are
        # linked up to the folders registered for this entity.
        # store this in a set so that we ensure a unique set of matches

        paths = set()
        pc = path_cache.PathCache(self.tk)
        path_ids = []
        paths = []
        try:
            for sg_fs_id in ids:
                # get path subtree for this id via the path cache
                for path_obj in pc.get_folder_tree_from_sg_id(sg_fs_id):
                    # store in the set as a tuple which is immutable
                    paths.append(path_obj["path"])
                    path_ids.append(path_obj["sg_id"])
        finally:
            pc.close()

        log.info("")
        log.info("The following folders will be unregistered:")
        for p in paths:
            log.info(" - %s" % p)

        log.info("")
        log.info(
            "Proceeding will unregister the above paths from Toolkit's path cache. "
            "This will not alter any of the content in the file system, but once you have "
            "unregistered the paths, they will not be recognized by PTR until you run "
            "Toolkit folder creation again."
        )
        log.info("")
        log.info(
            "This is useful if you have renamed an Asset or Shot and want to move its "
            "files to a new location on disk. In this case, start by unregistering the "
            "folders for the entity, then rename the Shot or Asset in Flow Production Tracking. "
            "Next, create new folders on disk using Toolkit's 'create folders' "
            "command. Finally, move the files to the new location on disk."
        )
        log.info("")
        if prompt:
            val = input(
                "Proceed with unregistering the above folders? (Yes/No) ? [Yes]: "
            )
            if val != "" and not val.lower().startswith("y"):
                log.info("Exiting! Nothing was unregistered.")
                return []

        log.info("Unregistering folders from Flow Production Tracking...")
        log.info("")

        path_cache.PathCache.remove_filesystem_location_entries(self.tk, path_ids)

        # lastly, another sync
        pc = path_cache.PathCache(self.tk)
        try:
            pc.synchronize()
        finally:
            pc.close()

        log.info("")
        log.info("Unregister complete. %s paths were unregistered." % len(paths))

        # now shuffle the return data into a list of dicts
        return_data = []
        for path_id, path in zip(path_ids, paths):
            return_data.append(
                {
                    "path": path,
                    "entity": {"type": path_cache.SHOTGUN_ENTITY, "id": path_id},
                }
            )

        return return_data
