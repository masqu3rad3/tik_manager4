# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from tank_vendor import yaml

from .. import LogManager
from ..errors import TankError

from . import filesystem
from . import ShotgunPath
from . import yaml_cache

log = LogManager.get_logger(__name__)


class StorageRoots(object):
    """
    This class provides a centralized interface and processing logic for the
    storage roots as specified in a configuration's config/core/roots.yml.
    The roots.yml defines the local storages in Shotgun that a configuration
    requires.

    Instances of this class can be instantiated by providing a config folder,
    under which roots are defined, or by providing the roots metadata itself
    as is common when creating the initial state of a configuration's roots
    (during setup).

    Methods are provided for accessing information about the configuration's
    storages as well as writing the roots definitions to disk.
    """

    ############################################################################
    # class data

    # the name of the fallback, legacy default storage name if one is not
    # defined explicitly in the roots file
    LEGACY_DEFAULT_STORAGE_NAME = "primary"

    # the relative path where storage roots are defined in a configuration
    STORAGE_ROOTS_FILE_PATH = os.path.join("core", "roots.yml")

    # sys.platform-specific path keys as expected in the root definitions
    PLATFORM_KEYS = ["mac_path", "linux_path", "windows_path"]

    ############################################################################
    # class methods

    @classmethod
    def file_exists(cls, config_folder):
        """
        Returns ``True`` if the configuration has a storage roots definition
        file. ``False`` otherwise.

        :param config_folder: The path to a config folder
        :rtype: bool
        """
        roots_file = os.path.join(config_folder, cls.STORAGE_ROOTS_FILE_PATH)
        return os.path.exists(roots_file)

    @classmethod
    def from_config(cls, config_folder):
        """
        Constructs a StorageRoots object from the supplied config folder.

        The supplied config folder may or may not define required storage roots,
        but the method will return a ``StorageRoots`` instance anyway.

        :param config_folder: The path to a config folder
        :returns: A ``StorageRoots`` object instance
        """

        log.debug("Creating StorageRoots instance from config: %s" % (config_folder,))
        storage_roots = cls()
        storage_roots._init_from_config(config_folder)
        log.debug("Created: %s" % (storage_roots,))

        return storage_roots

    @classmethod
    def from_metadata(cls, metadata):
        """
        Constructs a StorageRoots object from the supplied metadata.

        The supplied metadata should be a dictionary where the keys represent
        the names of storage roots and the values are dictionaries that define
        that storage.

        Example metadata dictionary::

            {
                "work": {
                    "description": "Storage root for artist work files",
                    "default": true,
                    "shotgun_storage_id": 123,
                    "linux_path": "/proj/work",
                    "mac_path": "/proj/work",
                    "windows_path": "\\\\proj\\work",
                },
                "data": {
                    "description": "Storage root for large data sets",
                    "default": false,
                    "shotgun_storage_id": 456,
                    "linux_path": "/studio/data",
                    "mac_path": "/studio/data",
                    "windows_path": "\\\\network\\data",
                }
            }

        :param metadata: The storage roots metadata this object wraps
        :returns: A ``StorageRoots`` object instance
        """

        log.debug("Creating StorageRoots instance from metadata: %s" % (metadata,))
        storage_roots = cls()
        storage_roots._process_metadata(metadata)
        log.debug("Created: %s" % (storage_roots,))

        return storage_roots

    @classmethod
    def write(cls, sg_connection, config_folder, storage_roots):
        """
        Given a ``StorageRoots`` object, write it's metadata to the standard
        roots location within the supplied config folder. The method will write
        the corresponding local storage paths to the file as defined in Shotgun.
        This action will overwrite any existing storage roots file defined by
        the configuration.

        :param sg_connection: An existing PTR connection, used to query local
            storage entities to ensure paths are up-to-date when the file is
            written.
        :param config_folder: The configuration folder under which the required
            roots file is written.
        :param storage_roots: A ``StorageRoots`` object instance that defines
            the required roots.
        """

        (local_storage_lookup, unmapped_roots) = storage_roots.get_local_storages(
            sg_connection
        )

        roots_file = os.path.join(config_folder, cls.STORAGE_ROOTS_FILE_PATH)

        log.debug("Writing storage roots to: %s" % (roots_file,))

        # raise an error if there are any roots that can not be mapped to PTR
        # local storage entries
        if unmapped_roots:
            raise TankError(
                "The following storages are defined by %s but can not be "
                "mapped to a local storage in Flow Production Tracking: %s"
                % (roots_file, ", ".join(unmapped_roots))
            )

        if os.path.exists(roots_file):
            # warn if this file already exists
            log.warning(
                "The file '%s' exists in the configuration "
                "but will be overwritten with an auto generated file." % (roots_file,)
            )

        # build up a new metadata dict
        roots_metadata = storage_roots.metadata

        for root_name, root_info in storage_roots:

            # get the cached PTR storage dict
            sg_local_storage = local_storage_lookup[root_name]

            # get the local storage as a ShotgunPath object
            storage_sg_path = ShotgunPath.from_shotgun_dict(sg_local_storage)

            # update the root's metadata with the dictionary of all
            # sys.platform-style paths
            root_info.update(storage_sg_path.as_shotgun_dict())

        log.debug("Writing storage roots metadata: %s" % (roots_metadata,))

        # write the new metadata to disk
        with filesystem.auto_created_yml(roots_file) as fh:
            yaml.safe_dump(roots_metadata, fh, default_flow_style=False)

        log.debug("Finished writing storage roots file: %s" % (roots_file,))

    ############################################################################
    # special methods

    def __init__(self):
        """
        Initialize the storage roots object.

        Instances should not be created directly. Use the ``from_config`` or
        ``from_metadata`` class methods to create ``StorageRoot`` instances.
        """

        # the path to the config folder
        self._config_root_folder = None

        # the path to the roots file
        self._storage_roots_file = None

        # the underlying metadata for the required storage roots
        self._storage_roots_metadata = {}

        # a lookup of storage root names to shotgun paths
        self._shotgun_paths_lookup = {}

        # the default storage name as determined when parsing the metadata
        self._default_storage_name = None

    def __iter__(self):
        """
        Allows iteration over each defined root name and corresponding metadata.

        Yields root names and corresponding metadata upon iteration.
        """
        for root_name, root_info in self._storage_roots_metadata.items():
            yield root_name, root_info

    def __repr__(self):
        """
        Returns a string representation of the object.
        """
        return "<StorageRoots folder:'%s', roots:'%s'>" % (
            self._config_root_folder,
            ",".join(self.required_roots),
        )

    ############################################################################
    # properties

    @property
    def as_shotgun_paths(self):
        """
        A dictionary mapping of storage root names to ShotgunPath objects

        :returns: A dictionary structure with an entry for each storage defined.
            The value of each is a ShotgunPath object for the storage's path
            on disk.

        Example return dictionary::

            {
                "primary"  : <ShotgunPath>,
                "textures" : <ShotgunPath>
            }
        """
        return self._shotgun_paths_lookup

    @property
    def default(self):
        """
        The name (``str``) of the default storage root.
        """
        return self._default_storage_name

    @property
    def default_path(self):
        """
        A ``ShotgunPath`` object for the configuration's default storage root.

        May be ``None`` if no default could be determined.
        """
        return self._shotgun_paths_lookup.get(self._default_storage_name)

    @property
    def metadata(self):
        """
        The required storage roots metadata dictionary.

        This is a dictionary representation of the contents of the file. See the
        ``from_metadata`` method to see the structure of this dictionary.
        """
        return self._storage_roots_metadata

    @property
    def roots_file(self):
        """
        The path (``str``) to the storage root file represented by this object.
        """
        return self._storage_roots_file

    @property
    def required_roots(self):
        """
        A list of all required storage root names (``str``) by this
        configuration.
        """
        return list(self._storage_roots_metadata.keys())

    ############################################################################
    # public methods

    def get_local_storages(self, sg_connection):
        """
        Returns a tuple of information about the required storage roots and how
        they map to local storages in PTR.

        The first item in the tuple is a dictionary of storage root names mapped
        to a corresponding dictionary of fields for a local storage defined in
        Shotgun.

        The second item is a list of storage roots required by the configuration
        that can not be mapped to a PTR local storage.

        Example return value::

            (
                {
                    "work": {
                        "code": "primary",
                        "type": "LocalStorage",
                        "id": 123
                        "linux_path": "/proj/work"
                        "mac_path": "/proj/work"
                        "windows_path": None
                    }
                    "data": {
                        "code": "data",
                        "type": "LocalStorage",
                        "id": 456
                        "linux_path": "/proj/data"
                        "mac_path": "/proj/data"
                        "windows_path": None
                    }
                },
                ["data2", "data3"]
            )

        In the example above, 4 storage roots are defined by the configuration:
        "work", "data", "data2", and "data3". The "work" and "data" roots can
        be associated with a PTR local storage. The other two roots have no
        corresponding local storage in PTR.

        :param: A shotgun connection
        :returns: A tuple of information about local storages mapped to the
            configuration's required storage roots.
        """

        log.debug(
            "Attempting to associate required storage roots with PTR local "
            "storages..."
        )

        # build a lookup of storage root name to local storages PTR dicts
        local_storage_lookup = {}

        # keep a list of storages that could not be mapped to a PTR local storage
        unmapped_root_names = []

        # query all local storages from PTR so we can store a lookup of roots
        # defined here to PTR storages

        # fields required for PTR local storage queries
        local_storage_fields = ["code", "id"]
        local_storage_fields.extend(ShotgunPath.SHOTGUN_PATH_FIELDS)

        # create the PTR connection and query
        log.debug("Querying PTR local storages...")
        sg_storages = sg_connection.find("LocalStorage", [], local_storage_fields)
        log.debug("Query returned %s storages." % (len(sg_storages)))

        # create lookups of storages by name and id for convenience. we'll check
        # against each root's shotgun_storage_id first, falling back to the
        # name if the id mapping field is not defined.
        sg_storages_by_id = {}
        sg_storages_by_name = {}
        for sg_storage in sg_storages:
            id = sg_storage["id"]
            name = sg_storage["code"]
            sg_storages_by_id[id] = sg_storage
            sg_storages_by_name[name] = sg_storage

        for root_name, root_info in self:

            # see if the shotgun storage id is specified explicitly in the
            # roots.yml file.
            root_storage_id = root_info.get("shotgun_storage_id")
            if root_storage_id and root_storage_id in sg_storages_by_id:
                # found a match. store it in the lookup
                sg_storage = sg_storages_by_id[root_storage_id]
                log.debug(
                    "Storage root %s explicitly associated with PTR local "
                    "storage id %s (%s)" % (root_name, root_storage_id, sg_storage)
                )
                local_storage_lookup[root_name] = sg_storage
                continue

            # if we're here, no storage is specified explicitly. fall back to
            # the storage name.
            if root_name in sg_storages_by_name:
                # found a match. store it in the lookup
                sg_storage = sg_storages_by_name[root_name]
                log.debug(
                    "Storage root %s matches PTR local storage with same name "
                    "(%s)" % (root_name, sg_storage)
                )
                local_storage_lookup[root_name] = sg_storage
                continue

            # if we're here, then we could not map the storage root to a local
            # storage in PTR
            log.warning(
                "Storage root %s could not be mapped to a PTR local storage"
                % (root_name,)
            )
            unmapped_root_names.append(root_name)

        # return a tuple of the processed info
        return local_storage_lookup, unmapped_root_names

    def populate_defaults(self):
        """
        This method ensures all sys.platforms are represented in all defined
        storage roots. If the platform key does not exist, it will be added to
        the metadata and set to None.

        If there are no roots defined, this method will create a default root
        definition.
        """

        if self.required_roots:
            # there are roots required by this configuration. ensure all are
            # populated with the expected platform keys
            for root_name, root_info in self:
                for platform_key in self.PLATFORM_KEYS:

                    if platform_key not in root_info:
                        # platform key not defined for root. add it
                        root_info[platform_key] = None
        else:

            # no roots required by this configuration. add a default storage
            # requirement
            root_name = self.LEGACY_DEFAULT_STORAGE_NAME
            root_info = {
                "description": "Default location where project data is stored.",
                "mac_path": "/studio/projects",
                "linux_path": "/studio/projects",
                "windows_path": "\\\\network\\projects",
                "default": True,
            }

            self._default_storage_name = root_name
            self._storage_roots_metadata[root_name] = root_info
            self._shotgun_paths_lookup[root_name] = ShotgunPath.from_shotgun_dict(
                root_info
            )

    def update_root(self, root_name, storage_data):
        r"""
        Given a required storage root name, update the object's storage
        metadata.

        The data is in the same form as the dict required for a root provided to
        the `from_metadata` factory class method. Example::

            {
                "description": "A top-level root folder for production data...",
                "mac_path": "/shotgun/prod",
                "linux_path": "/shotgun/prod",
                "windows_path": "C:\shotgun\prod",
                "default": True,
                "shotgun_storage_id": 1,
            }

        Not all fields are required to be specified. Only the supplied fields
        will be updated on the existing storage data.

        :param root_name: The name of a root to update.
        :param storage_data: A dctionary
        """

        if root_name in self._storage_roots_metadata:
            # update the existing root info
            self._storage_roots_metadata[root_name].update(storage_data)
        else:
            # add the root/storage info to the metadata
            self._storage_roots_metadata[root_name] = storage_data

        if storage_data.get("default", False):
            self._default_storage_name = root_name

        # update the cached ShotgunPath with the new root storage info
        self._shotgun_paths_lookup[root_name] = ShotgunPath.from_shotgun_dict(
            self._storage_roots_metadata[root_name]
        )

    ############################################################################
    # protected methods

    def _init_from_config(self, config_folder):
        """
        Initialize the internal object data with the required storage roots
        defined under the supplied config folder.

        :param config_folder: The path to a configuration
        """

        log.debug(
            "Initializing storage roots object. "
            "Supplied config folder: %s" % (config_folder,)
        )

        # ---- set some basic data for the object

        # the supplied roots folder, just in case
        self._config_root_folder = config_folder

        # the full path to the roots file for debugging/messages
        self._storage_roots_file = os.path.join(
            self._config_root_folder, self.STORAGE_ROOTS_FILE_PATH
        )

        log.debug(
            "Storage roots file defined in the config: %s" % (self._storage_roots_file,)
        )

        # load the roots file and store the metadata
        if os.path.exists(self._storage_roots_file):
            roots_metadata = _get_storage_roots_metadata(self._storage_roots_file)
        else:
            # file does not exist. we will initialize with an empty dict
            roots_metadata = {}

        self._process_metadata(roots_metadata)

    def _process_metadata(self, roots_metadata):
        """
        Processes the supplied roots metadata and populates the internal object
        data structures. This includes storing easy access to the default root
        and other commonly accessed information.

        :param dict roots_metadata: A dictonary of metadata to use to populate
            the object. See the ``from_metadata`` class method for more info.
        """

        log.debug("Storage roots metadata: %s" % (roots_metadata,))

        # store it on the object
        self._storage_roots_metadata = roots_metadata

        # ---- store information about the roots for easy access

        log.debug("Processing required storages defined by the config...")

        # iterate over each storage root required by the configuration. try to
        # identify the default root.
        for root_name, root_info in self:

            log.debug("Processing storage: %s - %s" % (root_name, root_info))

            # store a shotgun path for each root definition. sanitize path data
            # by passing it through the ShotgunPath object. if the configuration
            # has not been installed, these paths may be None.
            self._shotgun_paths_lookup[root_name] = ShotgunPath.from_shotgun_dict(
                root_info
            )

            # check to see if this root is marked as the default
            if root_info.get("default", False):
                log.debug(
                    "Storage root %s explicitly marked as the default." % (root_name,)
                )
                self._default_storage_name = root_name

        # no default storage root defined explicitly. try to identify one if
        # there are storage roots defined
        if self.required_roots and not self._default_storage_name:

            log.debug("No default storage explicitly defined...")

            # if there is only one, then that is the default
            if len(roots_metadata) == 1:
                sole_storage_root = list(roots_metadata.keys())[0]
                log.debug(
                    "Storage %s identified as the default root because it is "
                    "the only root required by the configuration" % (sole_storage_root,)
                )
                self._default_storage_name = sole_storage_root
            elif self.LEGACY_DEFAULT_STORAGE_NAME in roots_metadata:
                # legacy primary storage name defined. that is the default
                log.debug(
                    "Storage %s identified as the default root because it "
                    "matches the legacy default root name."
                    % (self.LEGACY_DEFAULT_STORAGE_NAME,)
                )
                self._default_storage_name = self.LEGACY_DEFAULT_STORAGE_NAME
            else:
                # default storage will be None
                log.warning(
                    "Unable to identify a default storage root in the config's "
                    "required storages."
                )


################################################################################
# internal util methods


def _get_storage_roots_metadata(storage_roots_file):
    """
    Parse the supplied storage roots file

    :param storage_roots_file: Path to the roots file.
    :return: The parsed metadata as a dictionary.
    """

    log.debug("Reading storage roots file form disk: %s" % (storage_roots_file,))

    try:
        # keep a handle on the raw metadata read from the roots file
        roots_metadata = (
            yaml_cache.g_yaml_cache.get(storage_roots_file, deepcopy_data=False) or {}
        )  # if file is empty, initialize with empty dict
    except Exception as e:
        raise TankError(
            "Looks like the roots file is corrupt. "
            "Please contact support! "
            "File: '%s'. "
            "Error: %s" % (storage_roots_file, e)
        )

    log.debug("Read metadata: %s" % (roots_metadata,))

    return roots_metadata
