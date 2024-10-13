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
Methods and classes for generating folders based on the high level schema scaffold.

Known constraints:
 - won't allow the same entity type to appear more than once in the path. (ie Asset > Sub Asset)

"""

from . import constants
from ..errors import TankError

from ..path_cache import PathCache


class FolderIOReceiver(object):
    """
    Class that encapsulates all the IO operations from the various folder classes.
    """

    def __init__(self, tk, preview, entity_type, entity_ids):
        """
        Constructor.

        :param tk: A tk api instance
        :param preview: boolean set to true if run in preview mode
        :param entity_type: string with the sg entity type from the main folder creation request
        :param entity_ids: list of ids of the sg object for which folder creation was requested.

        """
        self._tk = tk
        self._preview_mode = preview
        self._items = list()
        self._secondary_cache_entries = list()
        self._entity_type = entity_type
        self._entity_ids = entity_ids

    ####################################################################################
    # methods to call to actually execute the folder creation logic

    @classmethod
    def sync_path_cache(cls, tk, full_sync):
        """
        Synchronizes the path cache folders.
        This happens as part of execute_folder_creation(), but sometimes it is
        useful to be able to execute this as a separate process.

        :param tk: A tk API instance
        :param full_sync: Do a full sync
        :returns: A list of paths which were calculated to be created
        """
        path_cache = PathCache(tk)

        try:

            # now run the path cache synchronization and see if there are any folders which
            # should be created locally.
            remote_items = []

            # new items that were not locally available are returned
            # as a list of dicts with keys id, type, name, configuration and path
            rd = path_cache.synchronize(full_sync)

            # for each item we get back from the path cache synchronization,
            # issue a remote entity folder request and pass that down to
            # the folder creation hook. This way, folders can be auto created
            # across multiple locations if desirable.
            for i in rd:
                remote_items.append(
                    {
                        "action": "remote_entity_folder",
                        "path": i["path"],
                        "metadata": i["metadata"],
                        "entity": i["entity"],
                    }
                )

            if len(remote_items) > 0:
                # execute the actual I/O
                tk.execute_core_hook(
                    constants.PROCESS_FOLDER_CREATION_HOOK_NAME,
                    items=remote_items,
                    preview_mode=False,
                )

            # return all folders that were computed
            folders = []
            for i in remote_items:
                action = i.get("action")
                if action in [
                    "entity_folder",
                    "create_file",
                    "folder",
                    "remote_entity_folder",
                ]:
                    folders.append(i["path"])
                elif action == "copy":
                    folders.append(i["target_path"])

        finally:
            path_cache.close()

        return folders

    def execute_folder_creation(self):
        """
        Runs the actual folder execution.

        :returns: A list of paths which were calculated to be created
        """

        path_cache = PathCache(self._tk)

        try:
            # because the sync can make changes to the path cache, do not run in preview mode
            remote_items = []
            if not self._preview_mode:

                # request that the path cache is synced against shotgun
                # new items that were not locally available are returned
                # as a list of dicts with keys id, type, name, configuration and path
                rd = path_cache.synchronize()

                # for each item we get back from the path cache synchronization,
                # issue a remote entity folder request and pass that down to
                # the folder creation hook. This way, folders can be auto created
                # across multiple locations if desirable.
                for i in rd:
                    remote_items.append(
                        {
                            "action": "remote_entity_folder",
                            "path": i["path"],
                            "metadata": i["metadata"],
                            "entity": i["entity"],
                        }
                    )

            # put together a list of entries we should pass to the database
            db_entries = []

            for i in self._items:
                if i.get("action") == "entity_folder":
                    db_entries.append(
                        {
                            "entity": i["entity"],
                            "path": i["path"],
                            "primary": True,
                            "metadata": i["metadata"],
                        }
                    )

            for i in self._secondary_cache_entries:
                db_entries.append(
                    {
                        "entity": i["entity"],
                        "path": i["path"],
                        "primary": False,
                        "metadata": i["metadata"],
                    }
                )

            # now that we are synced up with all remote sites,
            # validate the data before we push it into the database.
            # to properly cover some edge cases
            try:
                path_cache.validate_mappings(db_entries)
            except TankError as e:
                # validation problems!
                # before we bubble up these errors to the caller, we need to
                # take care of any folders that were possibly created during
                # the syncing:
                if len(remote_items) > 0:
                    self._tk.execute_core_hook(
                        constants.PROCESS_FOLDER_CREATION_HOOK_NAME,
                        items=remote_items,
                        preview_mode=self._preview_mode,
                    )

                # ok folders created for synced stuff. Now re-raise validation error
                raise TankError("Folder creation aborted: %s" % e)

            # validation passed!
            # now request the IO operations to take place
            # note that we pass both the items that were created from syncing with remote
            # and the new folders that have been computed

            folder_creation_items = remote_items + self._items

            self._tk.execute_core_hook(
                constants.PROCESS_FOLDER_CREATION_HOOK_NAME,
                items=folder_creation_items,
                preview_mode=self._preview_mode,
            )

            # database data was validated, folders on disk created
            # finally store all our new data in the path cache and in shotgun
            if not self._preview_mode:
                path_cache.add_mappings(db_entries, self._entity_type, self._entity_ids)

            # return all folders that were computed
            folders = []
            for i in folder_creation_items:
                action = i.get("action")
                if action in [
                    "entity_folder",
                    "create_file",
                    "folder",
                    "remote_entity_folder",
                ]:
                    folders.append(i["path"])
                elif action == "copy":
                    folders.append(i["target_path"])

        finally:
            path_cache.close()

        return folders

    ####################################################################################
    # methods called by the folder classes

    def register_secondary_entity(self, path, entity, config_metadata):
        """
        Called when a secondary entity is registered. A secondary
        entity is when a path contains more than one entity association.
        For example, a Shot folder configured to use the name
        {code}_{sg_sequence.Sequence.code} is implicity also linked
        to the associated sequence entity. This is the secondary entity.

        :param path: The path on disk to register
        :param entity: The associated shotgun entitiy as a dictionary with type and id
        :param config_metadata: The configuration file contents used to drive the creation
        """
        self._secondary_cache_entries.append(
            {"path": path, "entity": entity, "metadata": config_metadata}
        )

    def make_folder(self, path, config_metadata):
        """
        Called by the folder creation classes when a normal simple folder
        is to be created.

        :param path: The path on disk to register
        :param config_metadata: The configuration file contents used to drive the creation
        """
        self._items.append(
            {"path": path, "metadata": config_metadata, "action": "folder"}
        )

    def make_entity_folder(self, path, entity, config_metadata):
        """
        Creates an entity folder, including any cache entries
        the entity parameter must be a dict with id, type and name.

        :param path: The path on disk to register
        :param entity: The associated shotgun entitiy as a dictionary with type and id
        :param config_metadata: The configuration file contents used to drive the creation
        """
        self._items.append(
            {
                "path": path,
                "metadata": config_metadata,
                "entity": entity,
                "action": "entity_folder",
            }
        )

    def copy_file(self, src_path, target_path, config_metadata):
        """
        Called by the folder creation classes when a file is to be copied

        :param src_path: The source path to copy
        :param target_path: The target path to copy
        :param config_metadata: The configuration file contents used to drive the creation
        """
        self._items.append(
            {
                "source_path": src_path,
                "target_path": target_path,
                "metadata": config_metadata,
                "action": "copy",
            }
        )

    def create_symlink(self, path, target, config_metadata):
        """
        Called by the folder creation classes when a symlink is to be created.

        :param path: path to the symlink that should be created
        :param target: symlink target
        :param metadata: configuration metadata from folder creation system
        """
        self._items.append(
            {
                "path": path,
                "target": target,
                "metadata": config_metadata,
                "action": "symlink",
            }
        )
