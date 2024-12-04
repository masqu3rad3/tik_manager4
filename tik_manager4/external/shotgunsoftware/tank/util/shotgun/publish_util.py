# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Utility methods related to Published Files in Shotgun
"""

from __future__ import with_statement

from ...log import LogManager
from ..shotgun_path import ShotgunPath
from .. import constants
from .. import login

log = LogManager.get_logger(__name__)


def get_entity_type_display_name(tk, entity_type_code):
    """
    Returns the display name for an entity type given its type name.
    For example, if a custom entity is named "Workspace" in the
    Shotgun preferences, but is addressed as "CustomEntity03" in the
    Shotgun API, this method will resolve the display name::

        >>> get_entity_type_display_name(tk, "CustomEntity03")
        'Workspace'

    .. note:: The recommended way to access this data is now via the
              globals module in the shotgunutils framework. For more information,
              see http://developer.shotgridsoftware.com/tk-framework-shotgunutils/shotgun_globals.html

    :param tk: :class:`~sgtk.Sgtk` instance
    :param entity_type_code: API entity type name
    :returns: display name
    """
    schema_data = tk.get_cache_item(constants.SHOTGUN_SCHEMA_CACHE_KEY)
    if schema_data is None:
        # now resolve the entity types into display names using the schema_entity_read method.
        schema_data = tk.shotgun.schema_entity_read()
        # returns a dictionary on the following form:
        # { 'Booking': {'name': {'editable': False, 'value': 'Booking'}}, ... }
        tk.set_cache_item(constants.SHOTGUN_SCHEMA_CACHE_KEY, schema_data)

    display_name = entity_type_code
    try:
        if entity_type_code in schema_data:
            display_name = schema_data[entity_type_code]["name"]["value"]
    except:
        pass

    return display_name


def get_cached_local_storages(tk):
    """
    Return a list of all Shotgun local storages.
    Use an in-memory cache for performance

    :param tk: :class:`~sgtk.Sgtk` instance
    :returns: List of shotgun entity dictionaries
    """
    storage_data = tk.get_cache_item(constants.SHOTGUN_LOCAL_STORAGES_CACHE_KEY)

    if storage_data is None:
        log.debug("Caching PTR local storages...")
        storage_data = tk.shotgun.find(
            "LocalStorage", [], ["id", "code"] + ShotgunPath.SHOTGUN_PATH_FIELDS
        )
        log.debug("...caching complete. Got %d storages." % len(storage_data))
        tk.set_cache_item(constants.SHOTGUN_LOCAL_STORAGES_CACHE_KEY, storage_data)

    return storage_data


@LogManager.log_timing
def find_publish(
    tk, list_of_paths, filters=None, fields=None, only_current_project=True
):
    """
    Finds publishes in Shotgun given paths on disk.
    This method is similar to the find method in the Shotgun API,
    except that instead of an Entity type, a list of files is
    passed into the function.

    In addition to a list of files, shotgun filters can also be specified.
    This may be useful if for example all publishes with a certain status
    should be retrieved.

    By default, the shotgun id is returned for each successfully identified path.
    If you want to retrieve additional fields, you can specify these using
    the fields parameter.

    By default, only publishes in the current project will be found. If you
    want to retreive publishes from any active project in the pipeline config,
    you can specify the only_current_project param to False.

    The method will return a dictionary, keyed by path. The value will be
    a standard shotgun query result dictionary, for example::

        {
            "/foo/bar" : { "id": 234, "type": "TankPublishedFile", "code": "some data" },
            "/foo/baz" : { "id": 23,  "type": "TankPublishedFile", "code": "some more data" }
        }

    Fields that are not found, or filtered out by the filters parameter,
    are not returned in the dictionary.

    :param tk: :class:`~sgtk.Sgtk` instance
    :param list_of_paths: List of full paths for which information should be retrieved
    :param filters: Optional list of shotgun filters to apply.
    :param fields: Optional list of fields from the matched entities to
                   return. Defaults to id and type.
    :param only_current_project: Optional boolean to find publishes in Shotgun only from the
                                 current project (True) or from any active project (False).
                                 Defaults to True.
    :returns: dictionary keyed by path
    """
    # avoid cyclic references
    from .publish_creation import group_by_storage

    # Map path caches to full paths, grouped by storage
    # in case of sequences, there will be more than one file
    # per path cache
    # {<storage name>: { path_cache: [full_path, full_path]}}
    storage_root_to_paths = group_by_storage(tk, list_of_paths, only_current_project)

    filters = filters or []
    fields = fields or []

    # make copy
    sg_fields = fields[:]
    # add these parameters to the fields list - they are needed for the internal processing
    # of the result set.
    sg_fields.append("created_at")
    sg_fields.append("path_cache")

    # PASS 1
    # because the file locations are split for each publish in shotgun into two fields
    # - the path_cache which is a storage relative, platform agnostic path
    # - a link to a storage entity
    # ...we need to group the paths per storage and then for each storage do a
    # shotgun query of the form find all records where path_cache, in, /foo, /bar, /baz etc.
    published_files = {}

    # get a list of all storages that we should look up.
    # for 0.12 backwards compatibility, add the Tank Storage.
    root_names = list(storage_root_to_paths.keys())
    if constants.PRIMARY_STORAGE_NAME in root_names:
        root_names.append("Tank")

    # get a lookup of required root to local storage
    (
        mapped_roots,
        unmapped_roots,
    ) = tk.pipeline_configuration.get_local_storage_mapping()

    published_file_entity_type = get_published_file_entity_type(tk)
    for root_name in root_names:

        local_storage = mapped_roots.get(root_name)
        if not local_storage:
            # fail gracefully here - it may be a storage which has been deleted
            published_files[root_name] = []
            continue

        # make copy
        sg_filters = filters[:]
        path_cache_filter = ["path_cache", "in"]

        # now get the list of normalized files for this storage
        # 0.12 backwards compatibility: if the storage name is Tank,
        # this is the same as the primary storage.
        if root_name == "Tank":
            normalized_paths = storage_root_to_paths[
                constants.PRIMARY_STORAGE_NAME
            ].keys()
        else:
            normalized_paths = storage_root_to_paths[root_name].keys()

        # add all of those to the query filter
        for path_cache_path in normalized_paths:
            path_cache_filter.append(path_cache_path)

        sg_filters.append(path_cache_filter)
        sg_filters.append(["path_cache_storage", "is", local_storage])

        # organize the returned data by storage
        published_files[root_name] = tk.shotgun.find(
            published_file_entity_type, sg_filters, sg_fields
        )

    # PASS 2
    # take the published_files structure, containing the shotgun data
    # grouped by storage, and turn that into the final data structure
    #
    matches = {}

    for local_storage_name, publishes in published_files.items():

        # get a dictionary which maps shotgun paths to file system paths
        if local_storage_name == "Tank":
            normalized_path_lookup_dict = storage_root_to_paths[
                constants.PRIMARY_STORAGE_NAME
            ]
        else:
            normalized_path_lookup_dict = storage_root_to_paths[local_storage_name]

        # now go through all publish entities found for current storage
        for publish in publishes:

            path_cache = publish["path_cache"]

            # get the list of real paths matching this entry
            for full_path in normalized_path_lookup_dict.get(path_cache, []):

                if full_path not in matches:
                    # this path not yet in the list of matching publish entity data
                    matches[full_path] = publish

                else:
                    # found a match! This is most likely because the same file
                    # has been published more than once. In this case, we return
                    # the entity data for the file that is more recent.
                    existing_publish = matches[full_path]
                    if existing_publish["created_at"] < publish["created_at"]:
                        matches[full_path] = publish

    # PASS 3 -
    # clean up resultset
    # note that in order to do this we have pulled in additional fields from
    # shotgun (path_cache, created_at etc) - unless these are specifically asked for
    # by the caller, get rid of them.
    #
    for path in matches:
        delete_fields = []
        # find fields
        for field in matches[path]:
            if field not in fields and field not in ("id", "type"):
                # field is not the id field and was not asked for.
                delete_fields.append(field)
        # remove fields
        for f in delete_fields:
            del matches[path][f]

    return matches


@LogManager.log_timing
def create_event_log_entry(tk, context, event_type, description, metadata=None):
    """
    Creates an event log entry inside of Shotgun.
    Event log entries can be handy if you want to track a process or a sequence of events.

    :param tk: :class:`~sgtk.Sgtk` instance
    :param context: A :class:`~sgtk.Context` to associate with the event log entry.

    :param event_type: String which defines the event type. The Shotgun standard suggests
                       that this should be of the form Company_Item_Action. Examples include::

                           Shotgun_Asset_New
                           Shotgun_Asset_Change
                           Shotgun_User_Login

    :param description: A verbose description explaining the meaning of this event.

    :param metadata: A dictionary of metadata information which will be attached to the event
                     log record in Shotgun. This dictionary may only contain simple data types
                     such as ints, strings etc.

    :returns: The newly created shotgun record
    """

    data = {}
    data["description"] = description
    data["event_type"] = event_type
    data["entity"] = context.entity
    data["project"] = context.project
    data["meta"] = metadata

    sg_user = login.get_current_user(tk)
    if sg_user:
        data["user"] = sg_user

    return tk.shotgun.create("EventLogEntry", data)


def get_published_file_entity_type(tk):
    """
    Return the entity type that this toolkit uses for its Publishes.

    .. note:: This is for backwards compatibility situations only.
              Code targeting new installations can assume that
              the published file type in Shotgun is always ``PublishedFile``.

    :param tk: :class:`~sgtk.Sgtk` instance
    :returns: "PublishedFile" or "TankPublishedFile"

    """
    return tk.pipeline_configuration.get_published_file_entity_type()
