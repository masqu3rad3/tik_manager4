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
Methods relating to the Path cache, a central repository where metadata about
all Tank items in the file system are kept.

"""

import collections
import sqlite3
import sys
import os
import itertools

# use api json to cover py 2.5
# todo - replace with proper external library
from tank_vendor import shotgun_api3
from tank_vendor import six
from tank_vendor.shotgun_api3.lib import sgsix
from tank_vendor.six.moves import range

json = shotgun_api3.shotgun.json

from .platform.engine import show_global_busy, clear_global_busy
from . import constants
from .errors import TankError
from . import LogManager
from .util.login import get_current_user

# Shotgun field definitions to store the path cache data
SHOTGUN_ENTITY = "FilesystemLocation"
SG_ENTITY_FIELD = "entity"
SG_PATH_FIELD = "path"
SG_METADATA_FIELD = "configuration_metadata"
SG_IS_PRIMARY_FIELD = "is_primary"
SG_ENTITY_ID_FIELD = "linked_entity_id"
SG_ENTITY_TYPE_FIELD = "linked_entity_type"
SG_ENTITY_NAME_FIELD = "code"
SG_PIPELINE_CONFIG_FIELD = "pipeline_configuration"

log = LogManager.get_logger(__name__)


class PathCache(object):
    """
    A global cache which holds the mapping between a shotgun entity and a location on disk.

    NOTE! This uses sqlite and the db is typically hosted on an NFS storage.
    Ensure that the code is developed with the constraints that this entails in mind.
    """

    # sqlite has a limit for how many items fit into a single in statement
    SQLITE_MAX_ITEMS_FOR_IN_STATEMENT = 200

    # To avoid paging, we batch queries of FilesystemLocation entities
    # in chunks of 500 and combine the results. The performance issues
    # around this have been largely alleviated in Shotgun 7.4.x and the
    # accompanying shotgun_api3 that was released at the same time, but
    # we still want to batch at the old page length of 500 to boost
    # performance when older PTR or API versions are used. We should
    # eventually raise this to 5000 (or more) when we feel it is safe
    # to do so.
    SHOTGUN_ENTITY_QUERY_BATCH_SIZE = 500

    def __init__(self, tk):
        """
        Constructor.

        :param tk: Toolkit API instance
        """
        self._connection = None
        self._tk = tk
        self._sync_with_sg = tk.pipeline_configuration.get_shotgun_path_cache_enabled()

        if tk.pipeline_configuration.has_associated_data_roots():
            self._path_cache_disabled = False
            self._init_db()
            self._roots = tk.pipeline_configuration.get_data_roots()
        else:
            # no primary location found. Path cache therefore does not exist!
            # go into a no-path-cache-mode
            self._path_cache_disabled = True

    def _init_db(self):
        """
        Sets up the database
        """
        # first, make way for the path cache file. This call
        # will ensure that there is a valid folder and file on
        # disk, created with all the right permissions etc.
        path_cache_file = self._get_path_cache_location()

        self._connection = sqlite3.connect(path_cache_file)

        # this is to handle unicode properly - make sure that sqlite returns
        # str objects for TEXT fields rather than unicode. Note that any unicode
        # objects that are passed into the database will be automatically
        # converted to UTF-8 strs, so this text_factory guarantees that any character
        # representation will work for any language, as long as data is either input
        # as UTF-8 (byte string) or unicode. And in the latter case, the returned data
        # will always be unicode.
        self._connection.text_factory = str

        c = self._connection.cursor()
        try:

            # get a list of tables in the current database
            ret = c.execute("SELECT name FROM main.sqlite_master WHERE type='table';")
            table_names = [x[0] for x in ret.fetchall()]

            if len(table_names) == 0:
                # we have a brand new database. Create all tables and indices

                # note that because some clients are writing to NFS storage, we
                # up the default page size somewhat (from 4k -> 8k) to improve
                # performance. See https://sqlite.org/pragma.html#pragma_page_size

                c.executescript(
                    """
                    PRAGMA page_size=8192;

                    CREATE TABLE path_cache (entity_type text, entity_id integer, entity_name text, root text, path text, primary_entity integer);

                    CREATE INDEX path_cache_entity ON path_cache(entity_type, entity_id);

                    CREATE INDEX path_cache_path ON path_cache(root, path, primary_entity);

                    CREATE UNIQUE INDEX path_cache_all ON path_cache(entity_type, entity_id, root, path, primary_entity);

                    CREATE TABLE event_log_sync (last_id integer);

                    CREATE TABLE shotgun_status (path_cache_id integer, shotgun_id integer);

                    CREATE UNIQUE INDEX shotgun_status_id ON shotgun_status(path_cache_id);

                    CREATE INDEX shotgun_status_shotgun_id ON shotgun_status(shotgun_id);
                    """
                )
                self._connection.commit()

            else:

                # we have an existing database! Ensure it is up to date
                if "event_log_sync" not in table_names:
                    # this is a pre-0.15 setup where the path cache does not have event log sync
                    c.executescript("CREATE TABLE event_log_sync (last_id integer);")
                    self._connection.commit()

                if "shotgun_status" not in table_names:
                    # this is a pre-0.15 setup where the path cache does not have the shotgun_status table
                    c.executescript(
                        """CREATE TABLE shotgun_status (path_cache_id integer, shotgun_id integer);
                                       CREATE UNIQUE INDEX shotgun_status_id ON shotgun_status(path_cache_id);"""
                    )
                    self._connection.commit()

                # now ensure that some key fields that have been added during the dev cycle are there
                ret = c.execute("PRAGMA table_info(path_cache)")
                field_names = [x[1] for x in ret.fetchall()]

                # check for primary entity field - this was added back in 0.12.x
                if "primary_entity" not in field_names:
                    c.executescript(
                        """
                        ALTER TABLE path_cache ADD COLUMN primary_entity integer;
                        UPDATE path_cache SET primary_entity=1;

                        DROP INDEX IF EXISTS path_cache_path;
                        CREATE INDEX IF NOT EXISTS path_cache_path ON path_cache(root, path, primary_entity);

                        DROP INDEX IF EXISTS path_cache_all;
                        CREATE UNIQUE INDEX IF NOT EXISTS path_cache_all ON path_cache(entity_type, entity_id, root, path, primary_entity);
                        """
                    )

                    self._connection.commit()

        finally:
            c.close()

    def _get_path_cache_location(self):
        """
        Creates the path cache file and returns its location on disk.

        :returns: The path to the path cache file
        """
        if self._tk.pipeline_configuration.get_shotgun_path_cache_enabled():

            # 0.15+ path cache setup - call out to a core hook to determine
            # where the path cache should be located.
            path = self._tk.execute_core_hook_method(
                constants.CACHE_LOCATION_HOOK_NAME,
                "get_path_cache_path",
                project_id=self._tk.pipeline_configuration.get_project_id(),
                # Do NOT use the plugin_id as a suffix for the path cache folder. This would
                # prevent a path cache sync from an engine to be reused by another plugiin.
                plugin_id=None,
                pipeline_configuration_id=self._tk.pipeline_configuration.get_shotgun_id(),
            )

        else:
            # old (v0.14) style path cache
            # fall back on the 0.14 setting, where the path cache
            # is located in a tank folder in the project root
            path = os.path.join(
                self._tk.pipeline_configuration.get_primary_data_root(),
                "tank",
                "cache",
                "path_cache.db",
            )

            # first check that the cache folder exists
            # note that the cache folder is inside of the tank folder
            # so no need to attempt a recursive creation here.
            cache_folder = os.path.dirname(path)
            if not os.path.exists(cache_folder):
                old_umask = os.umask(0)
                try:
                    os.mkdir(cache_folder, 0o777)
                finally:
                    os.umask(old_umask)

            # now try to write a placeholder file with open permissions
            if not os.path.exists(path):
                old_umask = os.umask(0)
                try:
                    fh = open(path, "wb")
                    fh.close()
                    os.chmod(path, 0o666)
                finally:
                    os.umask(old_umask)

        return path

    def _path_to_dbpath(self, relative_path):
        """
        converts a  relative path to a db path form

        /foo/bar --> /foo/bar
        \foo\bar --> /foo/bar
        """
        # normalize the path before checking the project
        # some tools on windows the / others \

        # normalize
        norm_path = relative_path.replace(os.sep, "/")
        return norm_path

    def _separate_root(self, full_path):
        """
        Determines project root path and relative path.

        :returns: root_name, relative_path
        """
        n_path = full_path.replace(os.sep, "/")
        # Deterimine which root
        root_name = None
        relative_path = None
        for cur_root_name, root_path in self._roots.items():
            n_root = root_path.replace(os.sep, "/")
            if n_path.lower().startswith(n_root.lower()):
                root_name = cur_root_name
                # chop off root
                relative_path = full_path[len(root_path) :]
                break

        if not root_name:

            storages_str = ",".join(list(self._roots.values()))

            raise TankError(
                "The path '%s' could not be split up into a project centric path for "
                "any of the storages %s that are associated with this "
                "project." % (full_path, storages_str)
            )

        return root_name, relative_path

    def _dbpath_to_path(self, root_path, dbpath):
        r"""
        converts a dbpath to path for the local platform

        linux:    /foo/bar --> /studio/proj/foo/bar
        windows:  /foo/bar --> \\studio\proj\foo\bar

        :param root_path: Project root path
        :param db_path: Relative path
        """
        # first make sure dbpath doesn't start with a /
        if dbpath.startswith("/"):
            dbpath = dbpath[1:]
        # convert slashes
        path_sep = dbpath.replace("/", os.sep)
        # and join with root
        full_path = os.path.join(root_path, path_sep)
        return os.path.normpath(full_path)

    def close(self):
        """
        Close the database connection.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    ############################################################################################
    # shotgun synchronization (PTR data pushed into path cache database)

    def synchronize(self, full_sync=False):
        """
        Ensure the local path cache is in sync with Shotgun.

        If the method decides to do a full sync, it will attempt to
        launch the busy overlay window.

        :param full_sync: Boolean to indicate that a full sync should be carried out.

        :returns: A list of remote items which were detected, created remotely
                  and not existing in this path cache. These are returned as a list of
                  dictionaries, each containing keys:
                    - entity
                    - metadata
                    - path
        """

        if self._path_cache_disabled:
            log.debug("This project does not have any associated folders.")
            return []

        if not self._sync_with_sg:
            log.debug("Folder synchronization is turned off for this project.")
            return []

        c = self._connection.cursor()

        try:

            # check if we should do a full sync
            if full_sync:
                return self._do_full_sync(c)

            # first get the last synchronized event log event.
            res = c.execute("SELECT max(last_id) FROM event_log_sync")
            # get first item in the data set
            data = list(res)[0]

            log.debug("Path cache sync tracking marker in local sqlite db: %r" % data)

            # expect back something like [(249660,)] for a running cache and [(None,)] for a clear
            if len(data) != 1 or data[0] is None:
                # we should do a full sync
                return self._do_full_sync(c)

            # we have an event log id - so check if there are any more recent events
            event_log_id = data[0]

            # note! We search for all events greater than the prev event_log_id-1.
            # this way, the first record returned should be the last record that was
            # synced. This is a way of detecting that the event log chain is not broken.
            # it could break for example if someone has culled the event log table and in
            # that case we should fall back on a full sync.

            log.debug(
                "Fetching create/delete folder event log "
                "entries >= id %s for project %s..."
                % (event_log_id, self._get_project_link())
            )

            # note that we return the records in ascending order, meaning that they get
            # "played back" in the same order as they were created.
            #
            # for a non-truncated event log table, the first record returned
            # by this query should be the last one previously processed by the
            # path cache (via the event_log_id variable)
            response = self._tk.shotgun.find(
                "EventLogEntry",
                [
                    [
                        "event_type",
                        "in",
                        ["Toolkit_Folders_Create", "Toolkit_Folders_Delete"],
                    ],
                    ["id", "greater_than", (event_log_id - 1)],
                    ["project", "is", self._get_project_link()],
                ],
                ["id", "meta", "event_type"],
                [{"field_name": "id", "direction": "asc"}],
            )

            log.debug("Got %s event log entries" % len(response))

            # count creation and deletion entries
            num_deletions = 0
            num_creations = 0
            for r in response:
                if r["event_type"] == "Toolkit_Folders_Create":
                    num_creations += 1
                if r["event_type"] == "Toolkit_Folders_Delete":
                    num_deletions += 1

            log.debug(
                "Event log contains %s creations and %s deletions"
                % (num_creations, num_deletions)
            )

            if len(response) == 0:
                # nothing in event log. Probably a truncated setup.
                log.debug(
                    "No sync information in the event log. Falling back on a full sync."
                )
                return self._do_full_sync(c)

            elif response[0]["id"] != event_log_id:
                # there is either no event log data at all or a gap
                # in the event log. Assume that some culling has occured and
                # fall back on a full sync
                log.debug(
                    "Local path cache tracking marker is %s. "
                    "First event log id returned is %s. It looks "
                    "like the event log has been truncated, so falling back "
                    "on a full sync." % (event_log_id, response[0]["id"])
                )
                return self._do_full_sync(c)

            elif len(response) == 1 and response[0]["id"] == event_log_id:
                # nothing has changed since the last sync
                log.debug(
                    "Path cache syncing not necessary - local folders already up to date!"
                )
                return []
            elif num_creations > 0 or num_deletions > 0:
                # we have a complete trail of increments.
                # note that we skip the current entity.
                log.debug("Full event log history traced. Running incremental sync.")
                return self._do_incremental_sync(c, response[1:])

            else:
                # should never be here
                raise Exception("Unknown error - please contact support.")

        finally:
            c.close()

    def _upload_cache_data_to_shotgun(self, data, event_log_desc):
        """
        Takes a standard chunk of Shotgun data and uploads it to Shotgun
        using a single batch statement. Then writes a single event log entry record
        which binds the created path records. Returns the id of this event log record.

        data needs to be a list of dicts with the following keys:
        - entity - std sg entity dict with name, id and type
        - primary - boolean to indicate if something is primary
        - metadata - metadata dict
        - path - local os path
        - path_cache_row_id - the path cache db row id for the entry

        :param data: List of dicts. See details above.
        :param event_log_desc: Description to add to the event log entry created.
        :returns: A tuple with (event_log_id, sg_id_lookup)
                  - event_log_id is the id for the event log entry which summarizes the
                    creation event.
                  - sg_id_lookup is a dictionary where the keys are path cache row ids
                    and the values are the newly created corresponding shotgun ids.
        """

        if self._tk.pipeline_configuration.is_unmanaged():
            # no pipeline config for this one
            pc_link = None
        else:
            pc_link = {
                "type": "PipelineConfiguration",
                "id": self._tk.pipeline_configuration.get_shotgun_id(),
            }

        sg_batch_data = []
        for d in data:

            # get a name for the clickable url in the path field
            # this will include the name of the storage
            root_name, relative_path = self._separate_root(d["path"])
            db_path = self._path_to_dbpath(relative_path)
            path_display_name = "[%s] %s" % (root_name, db_path)

            req = {
                "request_type": "create",
                "entity_type": SHOTGUN_ENTITY,
                "data": {
                    "project": self._get_project_link(),
                    "created_by": get_current_user(self._tk),
                    SG_ENTITY_FIELD: d["entity"],
                    SG_IS_PRIMARY_FIELD: d["primary"],
                    SG_PIPELINE_CONFIG_FIELD: pc_link,
                    SG_METADATA_FIELD: json.dumps(d["metadata"]),
                    SG_ENTITY_ID_FIELD: d["entity"]["id"],
                    SG_ENTITY_TYPE_FIELD: d["entity"]["type"],
                    SG_ENTITY_NAME_FIELD: d["entity"]["name"],
                    SG_PATH_FIELD: {"local_path": d["path"], "name": path_display_name},
                },
            }

            sg_batch_data.append(req)

        # push to shotgun in a single xact
        log.debug("Uploading %s path entries to Flow Production Tracking..." % len(sg_batch_data))

        try:
            response = self._tk.shotgun.batch(sg_batch_data)
        except Exception as e:
            raise TankError(
                "Critical! Could not update PTR with folder "
                "data. Please contact support. Error details: %s" % e
            )

        # now create a dictionary where input path cache rowid (path_cache_row_id)
        # is mapped to the shotgun ids that were just created
        def _rowid_from_filesystem_entity(fsl_entity):
            path = fsl_entity[SG_PATH_FIELD]["local_path"]
            for d in data:
                # We need to match not only the path but also the entity type when associating the FilesystemLocation
                # entities with the local cache's row ids, because Task folders generate two entries with the same
                # path, one for the Task and one for the Step.
                if (
                    d["path"] == path
                    and d["entity"]["type"] == fsl_entity["linked_entity_type"]
                ):
                    return d["path_cache_row_id"]
            raise TankError(
                "Could not resolve row id for path! Please contact support! "
                "trying to resolve path '%s'. Source data set: %s" % (path, data)
            )

        rowid_sgid_lookup = {}
        for sg_obj in response:
            sg_id = sg_obj["id"]
            pc_row_id = _rowid_from_filesystem_entity(sg_obj)
            rowid_sgid_lookup[pc_row_id] = sg_id

        # now register the created ids in the event log
        # this will later on be read by the synchronization
        # now, based on the entities we just created, assemble a metadata chunk that
        # the sync calls can use later on.
        meta = {}
        # the api version used is always useful to know
        meta["core_api_version"] = self._tk.version
        # shotgun ids created
        meta["sg_folder_ids"] = [x["id"] for x in response]

        sg_event_data = {}
        sg_event_data["event_type"] = "Toolkit_Folders_Create"
        sg_event_data["description"] = "Toolkit %s: %s" % (
            self._tk.version,
            event_log_desc,
        )
        sg_event_data["project"] = self._get_project_link()
        sg_event_data["entity"] = pc_link
        sg_event_data["meta"] = meta
        sg_event_data["user"] = get_current_user(self._tk)

        try:
            log.debug("Creating event log entry %s" % sg_event_data)
            response = self._tk.shotgun.create("EventLogEntry", sg_event_data)
        except Exception as e:
            raise TankError(
                "Critical! Could not update PTR with folder data event log "
                "history marker. Please contact support. Error details: %s" % e
            )

        # return the event log id which represents this uploaded slab
        return (response["id"], rowid_sgid_lookup)

    def _get_project_link(self):
        """
        Returns the project link dictionary.

        :returns: If we have a site configuration, None will be returned. Otherwise, a dictionary
            with keys "type" and "id" will be returned.
        """
        if self._tk.pipeline_configuration.is_site_configuration():
            return None
        else:
            return {
                "type": "Project",
                "id": self._tk.pipeline_configuration.get_project_id(),
            }

    def _do_full_sync(self, cursor):
        """
        Ensure the local path cache is in sync with Shotgun.

        Returns a list of remote items which were detected, created remotely
        and not existing in this path cache. These are returned as a list of
        dictionaries, each containing keys:
            - entity
            - metadata
            - path

        :param cursor: Sqlite database cursor
        """

        show_global_busy(
            "Hang on, Toolkit is preparing folders...",
            (
                "Toolkit is retrieving folder listings from PTR and ensuring that your "
                "setup is up to date. Hang tight while data is being downloaded..."
            ),
        )
        try:
            log.debug("Performing a complete PTR folder sync...")

            # find the max event log id. we will store this in the sync db later.
            sg_data = self._tk.shotgun.find_one(
                "EventLogEntry",
                [
                    [
                        "event_type",
                        "in",
                        ["Toolkit_Folders_Create", "Toolkit_Folders_Delete"],
                    ],
                    ["project", "is", self._get_project_link()],
                ],
                ["id"],
                [{"field_name": "id", "direction": "desc"}],
            )

            if sg_data is None:
                # event log was wiped or we haven't done any folder operations
                max_event_log_id = 0
            else:
                max_event_log_id = sg_data["id"]

            data = self._replay_folder_entities(cursor, max_event_log_id)

        finally:
            clear_global_busy()

        return data

    @classmethod
    def remove_filesystem_location_entries(cls, tk, path_ids):
        """
        Removes FilesystemLocation entries from the path cache.

        :param list path_ids: List of FilesystemLocation ids to remove.
        """

        sg_batch_data = []
        for pid in path_ids:
            req = {
                "request_type": "delete",
                "entity_type": SHOTGUN_ENTITY,
                "entity_id": pid,
            }
            sg_batch_data.append(req)

        try:
            tk.shotgun.batch(sg_batch_data)
        except Exception as e:
            raise TankError(
                "PTR reported an error while attempting to delete FilesystemLocation entities. "
                "Please contact support. Details: %s Data: %s" % (e, sg_batch_data)
            )

        # now register the deleted ids in the event log
        # this will later on be read by the synchronization
        # now, based on the entities we just deleted, assemble a metadata chunk that
        # the sync calls can use later on.

        if tk.pipeline_configuration.is_unmanaged():
            pc_link = None
        else:
            pc_link = {
                "type": "PipelineConfiguration",
                "id": tk.pipeline_configuration.get_shotgun_id(),
            }

        if tk.pipeline_configuration.is_site_configuration():
            project_link = None
        else:
            project_link = {
                "type": "Project",
                "id": tk.pipeline_configuration.get_project_id(),
            }

        meta = {}
        # the api version used is always useful to know
        meta["core_api_version"] = tk.version
        # shotgun ids created
        meta["sg_folder_ids"] = path_ids

        sg_event_data = {}
        sg_event_data["event_type"] = "Toolkit_Folders_Delete"
        sg_event_data["description"] = "Toolkit %s: Unregistered %s folders." % (
            tk.version,
            len(path_ids),
        )
        sg_event_data["project"] = project_link
        sg_event_data["entity"] = pc_link
        sg_event_data["meta"] = meta
        sg_event_data["user"] = get_current_user(tk)

        try:
            tk.shotgun.create("EventLogEntry", sg_event_data)
        except Exception as e:
            raise TankError(
                "PTR Reported an error while trying to write a Toolkit_Folders_Delete event "
                "log entry after having successfully removed folders. Please contact support for "
                "assistance. Error details: %s Data: %s" % (e, sg_event_data)
            )

    def _do_incremental_sync(self, cursor, sg_data):
        """
        Ensure the local path cache is in sync with Shotgun.

        Patch the existing cache with the events passed via sg_data.

        Assumptions:
        - sg_data list always contains some entries
        - sg_data list only contains Toolkit_Folders_Create records

        This is a list of dicts ordered by id from low to high (old to new),
        each with keys
            - id
            - meta
            - attribute_name

        Example of items:
        {'event_type': 'Toolkit_Folders_Create',
         'meta': {'core_api_version': 'HEAD',
                  'sg_folder_ids': [123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133]},
         'type': 'EventLogEntry',
         'id': 249240}

        :param cursor: Sqlite database cursor
        :param sg_data: see details above
        :returns: A list of remote items which were detected, created remotely
                  and not existing in this path cache. These are returned as a list of
                  dictionaries, each containing keys:
                    - entity
                    - metadata
                    - path
        """

        if len(sg_data) == 0:
            return []

        log.debug("Begin replaying FilesystemLocation entities locally...")

        # find the max event log id in sg_data. We will store this in the sync db later.
        max_event_log_id = max([x["id"] for x in sg_data])

        created_folder_ids = []
        for d in sg_data:
            log.debug("Looking at event log entry %s" % d)
            if d["event_type"] == "Toolkit_Folders_Create":
                # this is a creation request! Replay it on our database
                created_folder_ids.extend(d["meta"]["sg_folder_ids"])
        log.debug("Event log analysis complete.")

        log.debug("Doing an incremental sync.")

        # Retrieve all the newly created folders and rewire the result so it can be indexed by id.
        created_folder_entities = self._get_filesystem_location_entities(
            created_folder_ids
        )
        created_folder_entities = dict(
            (entity["id"], entity) for entity in created_folder_entities
        )

        new_items = []

        for event in sg_data:
            sg_folder_ids = event["meta"].get("sg_folder_ids")

            if event["event_type"] == "Toolkit_Folders_Delete":
                # Remove all the entries associated with that event.
                self._remove_filesystem_location_entities(cursor, sg_folder_ids)
            elif event["event_type"] == "Toolkit_Folders_Create":
                # For every folder in the create event.
                for folder_id in sg_folder_ids:
                    # If the entry is actually part of the end result, we'll add it!
                    if folder_id in created_folder_entities:
                        new_item = self._import_filesystem_location_entry(
                            cursor, created_folder_entities[folder_id]
                        )
                        # If the entry was actually imported.
                        if new_item:
                            new_items.append(new_item)

        self._update_last_event_log_synced(cursor, max_event_log_id)

        self._connection.commit()

        # run the actual sync - and at the end, inser the event_log_sync data marker
        # into the database to show where to start syncing from next time.
        return new_items

    def _get_filesystem_location_entities(self, folder_ids):
        """
        Retrieves filesystem location entities from Shotgun.

        :param list folder_ids: List of ids of entities to retrieve. If None, every entry is returned.

        :returns: List of FilesystemLocation entity dictionaries with keys:
            - id
            - type
            - configuration_metadata
            - is_primary
            - linked_entity_id
            - path
            - linked_entity_type
            - code
        """

        # get the ids that are missing from shotgun
        batches = []

        # We check specifically for a None here because it is a valid
        # use case to pass in an empty list of folder ids and get nothing
        # back in return as a result. Only in the case where we were
        # specifically given folder_ids=None would we fall back on
        # collecting all FilesystemLocation entities for the project.
        if folder_ids is not None:
            entity_filter = [["id", "in"]]
            batch_count = 0

            # Note: we batch the queries here. We want to avoid paging
            # for performance purposes when dealing with huge numbers
            # of entities (thousands+).
            for folder_id in folder_ids:
                if batch_count >= self.SHOTGUN_ENTITY_QUERY_BATCH_SIZE:
                    batches.append(entity_filter)
                    entity_filter = [["id", "in"]]
                    batch_count = 0

                entity_filter[0].append(folder_id)
                batch_count += 1

            # Take care of the last batch, which is likely below our
            # batch size and needs to be tacked onto the end.
            if batch_count > 0:
                batches.append(entity_filter)

            log.debug(
                "Getting FilesystemLocation entries for " "the following ids: %s",
                folder_ids,
            )
        else:
            project_entity = self._get_project_link()
            entity_filter = [["project", "is", project_entity]]
            batches.append(entity_filter)
            log.debug(
                "Getting all the project's FilesystemLocation entries. "
                "Project id: %s" % project_entity["id"]
            )

        sg_data = []

        for batched_filter in batches:
            sg_data.extend(
                self._tk.shotgun.find(
                    SHOTGUN_ENTITY,
                    batched_filter,
                    [
                        "id",
                        SG_METADATA_FIELD,
                        SG_IS_PRIMARY_FIELD,
                        SG_ENTITY_ID_FIELD,
                        SG_PATH_FIELD,
                        SG_ENTITY_TYPE_FIELD,
                        SG_ENTITY_NAME_FIELD,
                    ],
                    [{"field_name": "id", "direction": "asc"}],
                )
            )

        log.debug("...Retrieved %s records.", len(sg_data))

        return sg_data

    def _replay_folder_entities(self, cursor, max_event_log_id):
        """
        Downloads all the filesystem location entities from Shotgun and repopulates the
        path cache with them.

        Lastly, this method updates the event_log_sync marker in the sqlite database
        that tracks what the most recent event log id was being synced.

        :param cursor: Sqlite database cursor
        :param max_event_log_id: max event log marker to write to the path
                                 cache database after a full operation.
        :returns: A list of remote items which were detected, created remotely
                  and not existing in this path cache. These are returned as a list of
                  dictionaries, each containing keys:
                    - entity
                    - metadata
                    - path

        """
        log.debug("Fetching already registered folders from Flow Production Tracking...")

        sg_data = self._get_filesystem_location_entities(folder_ids=None)

        # complete sync - clear our tables first
        log.debug("Full sync - clearing local sqlite path cache tables...")
        cursor.execute("DELETE FROM event_log_sync")
        cursor.execute("DELETE FROM shotgun_status")
        cursor.execute("DELETE FROM path_cache")

        return_data = []

        for x in sg_data:
            imported_data = self._import_filesystem_location_entry(cursor, x)
            if imported_data:
                return_data.append(imported_data)

        # lastly, save the id of this event log entry for purpose of future syncing
        # note - we don't maintain a list of event log entries but just a single
        # value in the db, so start by clearing the table.

        self._update_last_event_log_synced(cursor, max_event_log_id)

        self._connection.commit()

        return return_data

    def _update_last_event_log_synced(self, cursor, event_log_id):
        """
        Saves into the db the last event processed from Shotgun.

        :param cursor: Database cursor.
        :type cursor: :class:`sqlite3.Cursor`
        :param int event_log_id: New last event log
        """
        log.debug("Inserting path cache marker %s in the sqlite db" % event_log_id)
        cursor.execute("DELETE FROM event_log_sync")
        cursor.execute("INSERT INTO event_log_sync(last_id) VALUES(?)", (event_log_id,))

    def _import_filesystem_location_entry(self, cursor, fsl_entity):
        """
        Imports a single filesystem location into the path cache.

        :param cursor: Database cursor.
        :type :class:`sqlite3.Cursor`
        :param dict fsl_entry: Filesystem location entity dictionary with keys:
            - id
            - type
            - configuration_metadata
            - is_primary
            - linked_entity_id
            - path
            - linked_entity_type
            - code
        """
        # get entity data from our entry
        entity = {
            "id": fsl_entity[SG_ENTITY_ID_FIELD],
            "name": fsl_entity[SG_ENTITY_NAME_FIELD],
            "type": fsl_entity[SG_ENTITY_TYPE_FIELD],
        }
        is_primary = fsl_entity[SG_IS_PRIMARY_FIELD]

        # note! If a local storage which is associated with a path is retired,
        # parts of the entity data returned by shotgun will be omitted.
        #
        # A valid, active path entry will be on the form:
        #  {'id': 653,
        #   'path': {'content_type': None,
        #            'id': 2186,
        #            'link_type': 'local',
        #            'local_path': '/Volumes/xyz/proj1/sequences/aaa',
        #            'local_path_linux': '/Volumes/xyz/proj1/sequences/aaa',
        #            'local_path_mac': '/Volumes/xyz/proj1/sequences/aaa',
        #            'local_path_windows': None,
        #            'local_storage': {'id': 2,
        #                              'name': 'primary',
        #                              'type': 'LocalStorage'},
        #            'name': '[primary] /sequences/aaa',
        #            'type': 'Attachment',
        #            'url': 'file:///Volumes/xyz/proj1/sequences/aaa'},
        #   'type': 'FilesystemLocation'},
        #
        # With a retired storage, the returned data from the PTR API is
        #  {'id': 646,
        #   'path': {'content_type': None,
        #            'id': 2141,
        #            'link_type': 'local',
        #            'local_storage': None,
        #            'name': '[primary] /sequences/aaa/missing',
        #            'type': 'Attachment'},
        #   'type': 'FilesystemLocation'},
        #

        # no path at all - this is an anomaly but handle it gracefully regardless
        if fsl_entity[SG_PATH_FIELD] is None:
            log.debug("No path associated with entry for %s. Skipping." % entity)
            return None

        # retired storage case - see above for details
        if fsl_entity[SG_PATH_FIELD].get("local_storage") is None:
            log.debug(
                "The storage for the path for %s has been deleted. Skipping." % entity
            )
            return None

        # get the local path from our attachment entity dict
        sg_local_storage_os_map = {
            "linux2": "local_path_linux",
            "win32": "local_path_windows",
            "darwin": "local_path_mac",
        }
        local_os_path_field = sg_local_storage_os_map[sgsix.platform]
        local_os_path = fsl_entity[SG_PATH_FIELD].get(local_os_path_field)

        # if the storage is not correctly configured for an OS, it is possible
        # that the path comes back as null. Skip such paths and report them in the log.
        if local_os_path is None:
            log.debug(
                "No local os path associated with entry for %s. Skipping." % entity
            )
            return None

        # if the path cannot be split up into a root_name and a leaf path
        # using the roots.yml file, log a warning and continue. This can happen
        # if roots files and storage setups change half-way through a project,
        # or if roots files are not in sync with the main storage definition
        # in this case, we want to just warn and skip rather than raise
        # an exception which will stop execution entirely.
        try:
            root_name, relative_path = self._separate_root(local_os_path)
        except TankError as e:
            log.debug("Could not resolve storages - skipping: %s" % e)
            return None

        # all validation checks seem ok - go ahead and make the changes.
        new_rowid = self._add_db_mapping(cursor, local_os_path, entity, is_primary)
        if new_rowid:
            # something was inserted into the db!
            # because this record came from shotgun, insert a record in the
            # shotgun_status table to indicate that this record exists in sg
            cursor.execute(
                "INSERT INTO shotgun_status(path_cache_id, shotgun_id) " "VALUES(?, ?)",
                (new_rowid, fsl_entity["id"]),
            )

            # and add this entry to our list of new things that we will return later on.
            return {
                "entity": entity,
                "path": local_os_path,
                "metadata": SG_METADATA_FIELD,
            }

        else:
            # Note: edge case - for some reason there was already an entry in the path cache
            # representing this. This could be because of duplicate entries and is
            # not necessarily an anomaly. It could also happen because a previos sync failed
            # at some point half way through.
            log.debug(
                "Found existing record for '%s', %s. Skipping."
                % (local_os_path, entity)
            )
            return None

    def _gen_param_string(self, items):
        """
        Creates a parametring string for SQL list based on the number of items in a list.

        If there are three items in the list, ?,?,? will be generated, If there is 5 items in
        the list, ?,?,?,?,? will be generated, and so on.

        :param list: Items for which we require a parameter string.
        """
        # Adapted from http://stackoverflow.com/a/1310001/1074536
        return ",".join(itertools.repeat("?", len(items)))

    def _remove_filesystem_location_entities(self, cursor, folder_ids):
        """
        Removes all the requested filesystem locations from the path cache.

        :param cursor: Database cursor.
        :type cursor: :class:`sqlite3.Cursor`
        :param list folder_ids: List of folder ids to remove from the path cache.
        """

        log.debug("Processing %s Toolkit_Folders_Delete events", len(folder_ids))

        def _chunks(large_list, chunk_size):
            """
            Helper operator to split a large list into smaller chunks
            """
            for i in range(0, len(large_list), chunk_size):
                yield large_list[i : i + chunk_size]

        # For every folder id, find the associated path cache id.
        all_path_cache_ids = []

        # split sql into batches - sqlite has a max number of terms for its in statement
        for subset_folder_ids in _chunks(
            folder_ids, self.SQLITE_MAX_ITEMS_FOR_IN_STATEMENT
        ):
            path_cache_ids = cursor.execute(
                "SELECT path_cache_id FROM shotgun_status "
                "WHERE shotgun_id IN (%s)" % self._gen_param_string(subset_folder_ids),
                subset_folder_ids,
            )

            # Flatten the list of one element tuples into a list of ids.
            path_cache_ids = [path_cache_id[0] for path_cache_id in path_cache_ids]

            # add to our full list
            all_path_cache_ids.extend(path_cache_ids)

        # Consider the following sequence
        # - Add 1
        # - Remove 1
        # - Add 2
        #
        # The final result is that only add 2 will be in the path cache.
        #
        # While incrementally updating the path cache, entry 1 will never be added to the path cache
        # because it doesn't exist in Shotgun anymore. Because of this, _import_filesystem_location_entry
        # will skip importing entry 1 because it isn't in the result final set of entities. When this
        # happens, it means that it also can't be removed from the path cache. As such, shotgun_status
        # will not report any mapping between the path cache and the Shotgun filesystem location
        # entity.
        if not all_path_cache_ids:
            return

        # Delete all the path cache entries associated with the file system locations.
        for subset_path_cache_ids in _chunks(
            all_path_cache_ids, self.SQLITE_MAX_ITEMS_FOR_IN_STATEMENT
        ):
            cursor.execute(
                "DELETE FROM path_cache where rowid IN (%s)"
                % self._gen_param_string(subset_path_cache_ids),
                subset_path_cache_ids,
            )

        # Now delete all the mappings between filesystem location entities and path cache entries.
        for subset_folder_ids in _chunks(
            folder_ids, self.SQLITE_MAX_ITEMS_FOR_IN_STATEMENT
        ):
            cursor.execute(
                "DELETE FROM shotgun_status WHERE shotgun_id IN (%s)"
                % self._gen_param_string(subset_folder_ids),
                subset_folder_ids,
            )

    ############################################################################################
    # pre-insertion validation

    def validate_mappings(self, data):
        """
        Checks a series of path mappings to ensure that they don't conflict with
        existing path cache data.

        :param data: list of dictionaries. Each dictionary should contain
                     the following keys:
                      - entity: a dictionary with keys name, id and type
                      - path: a path on disk
                      - primary: a boolean indicating if this is a primary entry
                      - metadata: configuration metadata
        """
        for d in data:
            self._validate_mapping(d["path"], d["entity"], d["primary"])

    def _validate_mapping(self, path, entity, is_primary):
        """
        Consistency checks happening prior to folder creation. May raise a TankError
        if an inconsistency is detected.

        :param path: The path calculated
        :param entity: Sg entity dict with keys id, type and name
        :param is_primary: indicates that this is a primary mapping - each folder may have
                           both primary and secondary entity associations - the secondary
                           being more loosely tied to the path.
        """

        # Make sure that there isn't already a record with the same
        # name in the database and file system, but with a different id.
        # We only do this for primary items - for secondary items, multiple items can exist
        if is_primary:
            entity_in_db = self.get_entity(path)

            if entity_in_db is not None:
                if (
                    entity_in_db["id"] != entity["id"]
                    or entity_in_db["type"] != entity["type"]
                ):

                    # there is already a record in the database for this path,
                    # but associated with another entity! Display an error message
                    # and ask that the user investigates using special tank commands.
                    #
                    # Note! We are only comparing against the type and the id
                    # not against the name. It should be perfectly valid to rename something
                    # in shotgun and if folders are then recreated for that item, nothing happens
                    # because there is already a folder which represents that item. (although now with
                    # an incorrect name)

                    msg = (
                        "The path '%s' cannot be processed because it is already associated "
                        % path
                    )
                    msg += "with %s '%s' (id %s) in Flow Production Tracking. " % (
                        entity_in_db["type"],
                        entity_in_db["name"],
                        entity_in_db["id"],
                    )
                    msg += (
                        "You are now trying to associate it with %s '%s' (id %s). "
                        % (entity["type"], entity["name"], entity["id"])
                    )
                    msg += "If you want to unregister your previously created folders, you can run "
                    msg += "the following command: 'tank unregister_folders %s' " % path
                    raise TankError(msg)

        # Check 2. Check if a folder for this shot has already been created,
        # but with another name. This can happen if someone
        # - creates a shot AAA
        # - creates folders on disk for Shot AAA
        # - renamed the shot to BBB
        # - tries to create folders. Now we don't want to create folders for BBB,
        #   since we already have a location on disk for this shot.
        #
        # note: this can also happen if the folder creation rules change.
        #
        # we only check for primary entities, doing the check for secondary
        # would only be to carry out the same check twice.
        if is_primary:
            for p in self.get_paths(entity["type"], entity["id"], primary_only=False):
                # so we got a path that matches our entity
                if p != path and os.path.dirname(p) == os.path.dirname(path):
                    # this path is identical to our path we are about to create except for the name.
                    # there is still a folder on disk. Abort folder creation
                    # with a descriptive error message
                    msg = "The path '%s' cannot be created because another " % path
                    msg += "path '%s' is already associated with %s %s. " % (
                        p,
                        entity["type"],
                        entity["name"],
                    )
                    msg += "This typically happens if an item in PTR is renamed or "
                    msg += "if the path naming in the folder creation configuration "
                    msg += "is changed. In order to continue you can either change "
                    msg += (
                        "the %s back to its previous name or you can unregister "
                        % entity["type"]
                    )
                    msg += "the currently associated folders by running the following command: "

                    # Steps are a special case. We need to tell the user to unregister the
                    # conflicting path directly rather than by entity. The reason for this is
                    # is two fold: running the unregister on the folder directly will properly
                    # handle the underlying Task folders beneath the Step. Also, we have some
                    # logic that assumes an entity being unregistered has a Project, and that
                    # isn't the case for Step entities. All in all, this is the right thing for
                    # a user to do to resolve the renamed Step entity's folder situation.
                    if entity["type"] == "Step":
                        msg += "'tank unregister_folders %s' and then try again." % p
                    else:
                        msg += "'tank %s %s unregister_folders' and then try again." % (
                            entity["type"],
                            entity["name"],
                        )
                    raise TankError(msg)

    ############################################################################################
    # database insertion methods

    def add_mappings(self, data, entity_type, entity_ids):
        """
        Adds a collection of mappings to the path cache in case they are not
        already there.

        :param data: list of dictionaries. Each dictionary contains
                     the following keys:
                      - entity: a dictionary with keys name, id and type
                      - path: a path on disk
                      - primary: a boolean indicating if this is a primary entry
                      - metadata: folder configuration metadata

        :param entity_type: sg entity type for the original high level folder creation
                            request that represents this series of mappings
        :param entity_ids: list of sg entity ids (ints) that represents which objects triggered
                           the high level folder creation request.

        """
        if self._path_cache_disabled:
            raise TankError(
                "You are currently running a configuration which does not have any "
                "capabilities of storing path entry lookups. There is no path cache "
                "file defined for this project."
            )

        c = self._connection.cursor()
        try:
            data_for_sg = []

            for d in data:
                new_rowid = self._add_db_mapping(
                    c, d["path"], d["entity"], d["primary"]
                )
                if new_rowid:
                    # this entry wasn't already in the db. So add it to the list to
                    # potentially upload to PTR later on
                    data_for_sg.append(d)
                    # append path cache row id to data
                    d["path_cache_row_id"] = new_rowid

            # now, if there were any FilesystemLocation records created,
            # create an event log entry that links back to those entries.
            # This is then used by the incremental path cache syncer.
            if self._sync_with_sg and len(data_for_sg) > 0:

                # first, a summary of what we are up to for the event log description
                entity_ids = ", ".join([str(x) for x in entity_ids])
                desc = "Created folders on disk for %ss with id: %s" % (
                    entity_type,
                    entity_ids,
                )

                # now push to shotgun
                (event_log_id, sg_id_lookup) = self._upload_cache_data_to_shotgun(
                    data_for_sg, desc
                )
                self._update_last_event_log_synced(c, event_log_id)
                # and indicate in the path cache that all these records have been pushed
                for (pc_row_id, sg_id) in sg_id_lookup.items():
                    c.execute(
                        "INSERT INTO shotgun_status(path_cache_id, shotgun_id) "
                        "VALUES(?, ?)",
                        (pc_row_id, sg_id),
                    )

        except:
            # error processing shotgun. Make sure we roll back the sqlite path cache
            # transaction
            self._connection.rollback()
            raise

        else:
            # Shotgun insert complete! Now we can commit path cache transaction
            self._connection.commit()

        finally:
            c.close()

    def _add_db_mapping(self, cursor, path, entity, primary):
        """
        Adds an association to the database. If the association already exists, it will
        do nothing, just return.

        If there is another association which conflicts with the association that is
        to be inserted, a TankError is raised.

        :param cursor: database cursor to use
        :param path: a path on disk representing the entity.
        :param entity: a shotgun entity dict with keys type, id and name
        :param primary: is this the primary entry for this particular path

        :returns: None if nothing was added to the db, otherwise the ROWID for the new row
        """

        if primary:
            # the primary entity must be unique: path/id/type
            # see if there are any records for this path
            # note that get_entity does not return secondary entities
            curr_entity = self.get_entity(path, cursor)

            if curr_entity is not None:
                # this path is already registered. Ensure it is connected to
                # our entity!
                #
                # Note! We are only comparing against the type and the id
                # not against the name. It should be perfectly valid to rename something
                # in shotgun and if folders are then recreated for that item, nothing happens
                # because there is already a folder which represents that item. (although now with
                # an incorrect name)
                #
                # also note that we have already done this once as part of the validation checks -
                # this time round, we are doing it more as an integrity check.
                #
                if (
                    curr_entity["type"] != entity["type"]
                    or curr_entity["id"] != entity["id"]
                ):
                    raise TankError(
                        "Database concurrency problems: The path '%s' is "
                        "already associated with PTR entity %s. Please re-run "
                        "folder creation to try again." % (path, str(curr_entity))
                    )

                else:
                    # the entry that exists in the db matches what we are trying to insert so skip it
                    return None

        else:
            # secondary entity
            # in this case, it is okay with more than one record for a path
            # but we don't want to insert the exact same record over and over again
            if self._is_path_in_db(path, entity["type"], entity["id"], cursor):
                # we already have the association present in the db.
                return None

        # there was no entity in the db. So let's create it!
        root_name, relative_path = self._separate_root(path)
        db_path = self._path_to_dbpath(relative_path)
        # note: the INSERT OR IGNORE INTO checks if we already have a
        # record in the db for this combination - if we do, the insert
        # is ignored. This is to avoid reported realtime issues when two
        # processes are doing an incremental sync at the same time,
        # download new data from shotgun and then attempts to insert it.
        cursor.execute(
            """INSERT OR IGNORE INTO path_cache(entity_type,
                                                 entity_id,
                                                 entity_name,
                                                 root,
                                                 path,
                                                 primary_entity)
                           VALUES(?, ?, ?, ?, ?, ?)""",
            (entity["type"], entity["id"], entity["name"], root_name, db_path, primary),
        )

        db_entity_id = cursor.lastrowid
        if db_entity_id == 0:
            # this has already been inserted into the db once
            # return None
            db_entity_id = None

        return db_entity_id

    def _is_path_in_db(self, path, entity_type, entity_id, cursor):
        """
        Given an entity, checks if a path is in the database or not

        :param path: Path to try
        :param entity_type: A Shotgun entity type
        :param entity_id: A Shotgun entity id
        :param cursor: Database cursor to use.
        :returns: True if path exists, false if not
        """
        try:
            root_name, relative_path = self._separate_root(path)
        except TankError:
            # fail gracefully if path is not a valid path
            # eg. doesn't belong to the project
            return False

        db_path = self._path_to_dbpath(relative_path)

        # now see if we have any records in the db which matches the path
        res = cursor.execute(
            """
            SELECT count(entity_id)
            FROM   path_cache
            WHERE  entity_type = ?
            AND    entity_id = ?
            AND    root = ?
            AND    path = ?
            GROUP BY entity_id
            """,
            (entity_type, entity_id, root_name, db_path),
        )

        res = list(res)

        # in case there are > 0 records: res = [(4,)]
        # in case there are no records: res = []
        if len(res) == 0:
            return False
        else:
            return True

    ############################################################################################
    # database accessor methods

    def get_shotgun_id_from_path(self, path):
        """
        Returns a FilesystemLocation id given a path.

        :param path: Path to look for in the path cache
        :returns: A shotgun FilesystemLocation id or None if not found.
        """

        try:
            root_path, relative_path = self._separate_root(path)
        except TankError:
            # fail gracefully if path is not a valid path
            # eg. doesn't belong to the project
            return None

        # use built in cursor unless specifically provided - means this
        # is part of a larger transaction
        c = self._connection.cursor()

        try:
            db_path = self._path_to_dbpath(relative_path)
            res = c.execute(
                """
                            select ss.shotgun_id
                            from shotgun_status ss
                            inner join path_cache pc on pc.rowid = ss.path_cache_id
                            where pc.path = ? and pc.root = ? and pc.primary_entity = 1
                            """,
                (db_path, root_path),
            )
            data = list(res)
        finally:
            c.close()

        if len(data) > 1:
            # never supposed to happen!
            raise TankError(
                "More than one entry in the path cache database for %s!" % path
            )

        elif len(data) == 1:
            return data[0][0]

        else:
            return None

    def get_folder_tree_from_sg_id(self, shotgun_id):
        """
        Returns a list of items making up the subtree below a certain shotgun id
        Each item in the list is a dictionary with keys path and sg_id.

        :param shotgun_id: The shotgun filesystem location id which should be unregistered.
        :returns: A list of items making up the subtree below the given id
        """
        c = self._connection.cursor()
        # first get the path
        res = c.execute(
            """SELECT pc.root, pc.path
                          FROM path_cache pc
                          INNER JOIN shotgun_status ss on pc.rowid = ss.path_cache_id
                          WHERE ss.shotgun_id = ? """,
            (shotgun_id,),
        )

        res = list(res)

        if len(res) == 0:
            return []

        matches = []

        # returns something like [('primary', '/assets/Character/foo')]
        root_name = res[0][0]
        path = res[0][1]
        # first append this match
        root_path = self._roots.get(root_name)
        matches.append(
            {"path": self._dbpath_to_path(root_path, path), "sg_id": shotgun_id}
        )

        # now get all paths that are child paths
        like_path = "%s/%%" % path
        res = c.execute(
            """SELECT pc.root, pc.path, ss.shotgun_id
                          FROM path_cache pc
                          INNER JOIN shotgun_status ss on pc.rowid = ss.path_cache_id
                          WHERE root = ? and path like ?""",
            (root_name, like_path),
        )

        for x in list(res):
            root_name = x[0]
            path = x[1]
            sg_id = x[2]
            # first append this match
            root_path = self._roots.get(root_name)
            matches.append(
                {"path": self._dbpath_to_path(root_path, path), "sg_id": sg_id}
            )

        return matches

    def get_paths(self, entity_type, entity_id, primary_only, cursor=None):
        """
        Returns a path given a shotgun entity (type/id pair)

        :param entity_type: A Shotgun entity type
        :param entity_id: A Shotgun entity id
        :param primary_only: Only return items marked as primary
        :param cursor: Database cursor to use. If none, a new cursor will be created.
        :returns: A path on disk
        """

        if self._path_cache_disabled:
            # no entries because we don't have a path cache
            return []

        paths = []

        # use built in cursor unless specifically provided - means this
        # is part of a larger transaction
        c = cursor or self._connection.cursor()

        try:
            if primary_only:
                res = c.execute(
                    "SELECT root, path FROM path_cache WHERE entity_type = ? AND entity_id = ? and primary_entity = 1",
                    (entity_type, entity_id),
                )
            else:
                res = c.execute(
                    "SELECT root, path FROM path_cache WHERE entity_type = ? AND entity_id = ?",
                    (entity_type, entity_id),
                )

            for row in res:
                root_name = row[0]
                relative_path = row[1]

                root_path = self._roots.get(root_name)
                if not root_path:
                    # The root name doesn't match a recognized name, so skip this entry
                    continue

                # assemble path
                path_str = self._dbpath_to_path(root_path, relative_path)
                paths.append(path_str)
        finally:
            if cursor is None:
                c.close()

        return paths

    def get_entity(self, path, cursor=None):
        """
        Returns an entity given a path.

        If this path is made up of nested entities (e.g. has a folder creation expression
        on the form Shot: "{code}_{sg_sequence.Sequence.code}"), the primary entity (in
        this case the Shot) will be returned.

        Note that if the lookup fails, none is returned.

        :param path: a path on disk
        :param cursor: Database cursor to use. If none, a new cursor will be created.
        :returns: Shotgun entity dict, e.g. {"type": "Shot", "name": "xxx", "id": 123}
                  or None if not found
        """
        if self._path_cache_disabled:
            # no entries because we don't have a path cache
            return None

        if path is None:
            # basic sanity checking
            return None

        try:
            root_path, relative_path = self._separate_root(path)
        except TankError:
            # fail gracefully if path is not a valid path
            # eg. doesn't belong to the project
            return None

        # use built in cursor unless specifically provided - means this
        # is part of a larger transaction
        c = cursor or self._connection.cursor()

        try:
            db_path = self._path_to_dbpath(relative_path)
            res = c.execute(
                "SELECT entity_type, entity_id, entity_name FROM path_cache WHERE path = ? AND root = ? and primary_entity = 1",
                (db_path, root_path),
            )
            data = list(res)
        finally:
            if cursor is None:
                c.close()

        if len(data) > 1:
            # never supposed to happen!
            raise TankError("More than one entry in path database for %s!" % path)
        elif len(data) == 1:
            # convert to string, not unicode!
            type_str = str(data[0][0])
            name_str = str(data[0][2])
            return {"type": type_str, "id": data[0][1], "name": name_str}
        else:
            return None

    def get_secondary_entities(self, path):
        """
        Returns all the secondary entities for a path.

        :param path: a path on disk
        :returns: list of shotgun entity dicts, e.g. [{"type": "Shot", "name": "xxx", "id": 123}]
                  or [] if no entities associated.
        """

        if self._path_cache_disabled:
            # no entries because we don't have a path cache
            return []

        try:
            root_path, relative_path = self._separate_root(path)
        except TankError:
            # fail gracefully if path is not a valid path
            # eg. doesn't belong to the project
            return []

        c = self._connection.cursor()
        try:
            db_path = self._path_to_dbpath(relative_path)
            res = c.execute(
                "SELECT entity_type, entity_id, entity_name FROM path_cache WHERE path = ? AND root = ? and primary_entity = 0",
                (db_path, root_path),
            )
            data = list(res)
        finally:
            c.close()

        matches = []
        for d in data:
            # convert to string, not unicode!
            type_str = str(d[0])
            name_str = str(d[2])
            matches.append({"type": type_str, "id": d[1], "name": name_str})

        return matches

    def ensure_all_entries_are_in_shotgun(self):
        """
        Ensures that all the path cache data in this database is also registered in Shotgun.

        This will go through each entity in the path cache database and check if it exists in
        Shotgun. If not, it will be created.

        No updates will be made to the path cache database.
        """

        SG_BATCH_SIZE = 50

        log.info("")
        log.info("Step 1 - Downloading current path data from Flow Production Tracking...")

        sg_data = self._tk.shotgun.find(
            SHOTGUN_ENTITY,
            [["project", "is", self._get_project_link()]],
            [SG_PATH_FIELD, SG_ENTITY_TYPE_FIELD, SG_ENTITY_ID_FIELD],
        )
        log.info(" - Got %s records." % len(sg_data))

        # reshuffle these into a dictionary based on path and entity type
        # this is so we can do fast lookups later
        sg_existing_data = {}
        for p in sg_data:
            local_path = p[SG_PATH_FIELD].get(
                "local_path"
            )  # using get() in case key is missing
            # key dictionary by local path, entity type and entity id. This is so that we can
            # handle secondary entities correctly.
            dict_key = (local_path, p[SG_ENTITY_TYPE_FIELD], p[SG_ENTITY_ID_FIELD])
            sg_existing_data[dict_key] = p["id"]

        # free up memory
        sg_data = None

        cursor = self._connection.cursor()

        try:
            # get all records and check each one against shotgun.
            pc_data = list(
                cursor.execute(
                    """select pc.rowid,
                                                    pc.entity_type,
                                                    pc.entity_id,
                                                    pc.entity_name,
                                                    pc.root,
                                                    pc.path,
                                                    pc.primary_entity
                                             from path_cache pc"""
                )
            )
        finally:
            cursor.close()

        log.info("")
        log.info("Step 2 - Loading path cache data...")
        log.info(" - %s paths loaded." % len(pc_data))

        log.info("")
        log.info("Step 3 - Culling paths already in Flow Production Tracking.")

        sg_records = []

        # cull stuff that already exists in shotgun
        for sql_record in pc_data:
            log.debug("Processing db record %s..." % str(sql_record))

            # resolve a local path from a root and a generic path
            root_name = sql_record[4]
            db_path = sql_record[5]
            root_path = self._roots.get(root_name)
            if not root_path:
                # The root name doesn't match a recognized name, so skip this entry
                log.debug(
                    "Skipping path '%s %s' which doesn't have a valid root."
                    % (root_name, db_path)
                )
                continue

            local_os_path = self._dbpath_to_path(root_path, db_path)

            entity_type = sql_record[1]
            entity_id = sql_record[2]

            # see if we have this in shotgun already
            sg_dict_key = (local_os_path, entity_type, entity_id)

            # now check if we have any entry in the path cache already which has that path
            if sg_dict_key in sg_existing_data:
                log.info(" - Skipping '%s'" % local_os_path)
                log.debug(
                    "Path '%s' (%s %s) is already in PTR (id %s)"
                    % (
                        local_os_path,
                        entity_type,
                        entity_id,
                        sg_existing_data[sg_dict_key],
                    )
                )
            else:

                # ok this record needs uploading and seems valid.
                sg_record = {}
                sg_record["entity"] = {}
                sg_record["entity"]["type"] = sql_record[1]
                sg_record["entity"]["id"] = sql_record[2]
                sg_record["entity"]["name"] = sql_record[3]
                sg_record["path"] = local_os_path
                sg_record["primary"] = bool(sql_record[6])
                sg_record["metadata"] = {}
                sg_record["path_cache_row_id"] = sql_record[0]
                sg_records.append(sg_record)

        # cull out stuff where the linked entity has been retired in shogun
        log.info("")
        log.info("Step 4 - Ensuring all PTR entity links are valid.")

        ids_to_look_for = collections.defaultdict(list)
        for sg_record in sg_records:
            # look up all items in shotgun.
            # group stuff by entity type
            ids_to_look_for[sg_record["entity"]["type"]].append(sg_record)

        # now query shotgun for each of the types
        ids_in_shotgun = {}
        sg_valid_records = []
        for (et, sg_records_for_et) in six.iteritems(ids_to_look_for):

            log.info(" - Checking %s %ss in Flow Production Tracking..." % (len(sg_records_for_et), et))

            # get the ids from shotgun for the current et.
            sg_ids = [x["entity"]["id"] for x in sg_records_for_et]
            ids = self._tk.shotgun.find(et, [["id", "in", sg_ids]])
            # note the use of set here to make lookups O(1) later
            raw_ids = set([x["id"] for x in ids])

            # check all our records for et and see if they have a match
            for sg_record in sg_records_for_et:
                if sg_record["entity"]["id"] in raw_ids:
                    sg_valid_records.append(sg_record)
                else:
                    log.info(
                        " - %s %s has been deleted in Flow Production Tracking. "
                        % (et, sg_record["entity"]["id"])
                    )

        # batch it and push it. All records should now be valid
        if len(sg_valid_records) > 0:
            log.info("")
            log.info("Step 5 - Uploading path entries to shotgun.")
            sg_batches = [
                sg_valid_records[x : x + SG_BATCH_SIZE]
                for x in range(0, len(pc_data), SG_BATCH_SIZE)
            ]
            event_log_description = "Path cache migration."
            for batch_idx, curr_batch in enumerate(sg_batches):
                log.info(
                    "Uploading batch %d/%d to Flow Production Tracking..."
                    % (batch_idx + 1, len(sg_batches))
                )
                self._upload_cache_data_to_shotgun(curr_batch, event_log_description)

        log.info("")
        log.info(
            "Migration complete. %s records created in Flow Production Tracking" % len(sg_valid_records)
        )
