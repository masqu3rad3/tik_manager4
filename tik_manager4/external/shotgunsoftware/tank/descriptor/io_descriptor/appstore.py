# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Toolkit App Store Descriptor.
"""

import os
from tank_vendor.six.moves import urllib
import fnmatch
from tank_vendor.six.moves import http_client
from tank_vendor.shotgun_api3.lib import httplib2

from ...util import shotgun
from ...util import pickle
from ...util import UnresolvableCoreConfigurationError, ShotgunAttachmentDownloadError
from ...util.user_settings import UserSettings

from ..errors import TankAppStoreConnectionError
from ..errors import TankAppStoreError
from ..errors import TankDescriptorError
from ..errors import InvalidAppStoreCredentialsError

from ... import LogManager
from .. import constants
from .downloadable import IODescriptorDownloadable

from ...constants import SUPPORT_URL

# use api json to cover py 2.5
from tank_vendor import shotgun_api3
from tank_vendor import six

json = shotgun_api3.shotgun.json

log = LogManager.get_logger(__name__)


# file where we cache the app store metadata for an item
METADATA_FILE = ".cached_metadata.pickle"


class IODescriptorAppStore(IODescriptorDownloadable):
    """
    Represents a toolkit app store item.

    {type: app_store, name: tk-core, version: v12.3.4}
    {type: app_store, name: NAME, version: VERSION}

    """

    # cache app store connections for performance
    _app_store_connections = {}

    # internal app store mappings
    (APP, FRAMEWORK, ENGINE, CONFIG, CORE) = range(5)

    _APP_STORE_OBJECT = {
        constants.DESCRIPTOR_APP: constants.TANK_APP_ENTITY_TYPE,
        constants.DESCRIPTOR_FRAMEWORK: constants.TANK_FRAMEWORK_ENTITY_TYPE,
        constants.DESCRIPTOR_ENGINE: constants.TANK_ENGINE_ENTITY_TYPE,
        constants.DESCRIPTOR_CONFIG: constants.TANK_CONFIG_ENTITY_TYPE,
        constants.DESCRIPTOR_INSTALLED_CONFIG: None,
        constants.DESCRIPTOR_CORE: None,
    }

    _APP_STORE_VERSION = {
        constants.DESCRIPTOR_APP: constants.TANK_APP_VERSION_ENTITY_TYPE,
        constants.DESCRIPTOR_FRAMEWORK: constants.TANK_FRAMEWORK_VERSION_ENTITY_TYPE,
        constants.DESCRIPTOR_ENGINE: constants.TANK_ENGINE_VERSION_ENTITY_TYPE,
        constants.DESCRIPTOR_CONFIG: constants.TANK_CONFIG_VERSION_ENTITY_TYPE,
        constants.DESCRIPTOR_INSTALLED_CONFIG: None,
        constants.DESCRIPTOR_CORE: constants.TANK_CORE_VERSION_ENTITY_TYPE,
    }

    _APP_STORE_LINK = {
        constants.DESCRIPTOR_APP: "sg_tank_app",
        constants.DESCRIPTOR_FRAMEWORK: "sg_tank_framework",
        constants.DESCRIPTOR_ENGINE: "sg_tank_engine",
        constants.DESCRIPTOR_CONFIG: "sg_tank_config",
        constants.DESCRIPTOR_INSTALLED_CONFIG: None,
        constants.DESCRIPTOR_CORE: None,
    }

    _DOWNLOAD_STATS_EVENT_TYPE = {
        constants.DESCRIPTOR_APP: "TankAppStore_App_Download",
        constants.DESCRIPTOR_FRAMEWORK: "TankAppStore_Framework_Download",
        constants.DESCRIPTOR_ENGINE: "TankAppStore_Engine_Download",
        constants.DESCRIPTOR_CONFIG: "TankAppStore_Config_Download",
        constants.DESCRIPTOR_INSTALLED_CONFIG: None,
        constants.DESCRIPTOR_CORE: "TankAppStore_CoreApi_Download",
    }

    _VERSION_FIELDS_TO_CACHE = [
        "id",
        "code",
        "sg_status_list",
        "description",
        "tags",
        "sg_detailed_release_notes",
        "sg_documentation",
        constants.TANK_CODE_PAYLOAD_FIELD,
    ]

    _BUNDLE_FIELDS_TO_CACHE = [
        "id",
        "sg_system_name",
        "sg_status_list",
        "sg_deprecation_message",
    ]

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: descriptor dictionary describing the bundle
        :param sg_connection: Shotgun connection to associated site
        :param bundle_type: Either Descriptor.APP, CORE, ENGINE or FRAMEWORK or CONFIG
        :return: Descriptor instance
        """
        super(IODescriptorAppStore, self).__init__(
            descriptor_dict, sg_connection, bundle_type
        )

        self._validate_descriptor(
            descriptor_dict, required=["type", "name", "version"], optional=["label"]
        )

        self._sg_connection = sg_connection
        self._bundle_type = bundle_type
        self._name = descriptor_dict.get("name")
        self._version = descriptor_dict.get("version")
        self._label = descriptor_dict.get("label")

    def __str__(self):
        """
        Human readable representation
        """
        display_name_lookup = {
            constants.DESCRIPTOR_APP: "App",
            constants.DESCRIPTOR_FRAMEWORK: "Framework",
            constants.DESCRIPTOR_ENGINE: "Engine",
            constants.DESCRIPTOR_CONFIG: "Config",
            constants.DESCRIPTOR_CORE: "Core",
        }

        # Toolkit App Store App tk-multi-loader2 v1.2.3
        # Toolkit App Store Framework tk-framework-shotgunutils v1.2.3
        # Toolkit App Store Core v1.2.3
        if self._bundle_type == constants.DESCRIPTOR_CORE:
            display_name = "Toolkit App Store Core %s" % self._version
        else:
            display_name = display_name_lookup[self._bundle_type]
            display_name = "Toolkit App Store %s %s %s" % (
                display_name,
                self._name,
                self._version,
            )

        if self._label:
            display_name += " [label %s]" % self._label

        return display_name

    def __load_cached_app_store_metadata(self, path):
        """
        Loads the metadata for a path in the app store

        :param path: path to bundle location on disk
        :return: metadata dictionary or None if not found
        """
        cache_file = os.path.join(path, METADATA_FILE)
        if os.path.exists(cache_file):
            fp = open(cache_file, "rb")
            try:
                metadata = pickle.load(fp)
            finally:
                fp.close()
        else:
            log.debug(
                "%r Could not find cached metadata file %s - "
                "will proceed with empty app store metadata." % (self, cache_file)
            )
            metadata = {}

        return metadata

    @LogManager.log_timing
    def __refresh_metadata(self, path, sg_bundle_data=None, sg_version_data=None):
        """
        Refreshes the metadata cache on disk. The metadata cache contains
        app store information such as deprecation status, label information
        and release note data.

        For performance, the metadata can be provided by the caller. If
        not provided, the method will retrieve it from the app store.

        If the descriptor resides in a read-only bundle cache, for example
        baked into a DCC distribution, the cache will not be updated.

        :param path: The path to the bundle where cache info should be written
        :param sg_bundle_data, sg_version_data: Shotgun data to cache
        :returns: A dictionary with keys 'sg_bundle_data' and 'sg_version_data',
                  containing Shotgun metadata.
        """
        log.debug("Attempting to refresh app store metadata for %r" % self)

        cache_file = os.path.join(path, METADATA_FILE)
        log.debug("Will attempt to refresh cache in %s" % cache_file)

        if (
            sg_version_data
        ):  # no none-check for sg_bundle_data param since this is none for tk-core
            log.debug("Will cache pre-fetched cache data.")
        else:
            log.debug("Connecting to PTR to retrieve metadata for %r" % self)

            # get the appropriate shotgun app store types and fields
            bundle_entity_type = self._APP_STORE_OBJECT[self._bundle_type]
            version_entity_type = self._APP_STORE_VERSION[self._bundle_type]
            link_field = self._APP_STORE_LINK[self._bundle_type]

            # connect to the app store
            (sg, _) = self.__create_sg_app_store_connection()

            if self._bundle_type == self.CORE:
                # special handling of core since it doesn't have a high-level 'bundle' entity
                sg_bundle_data = None

                sg_version_data = sg.find_one(
                    constants.TANK_CORE_VERSION_ENTITY_TYPE,
                    [["code", "is", self._version]],
                    self._VERSION_FIELDS_TO_CACHE,
                )
                if sg_version_data is None:
                    raise TankDescriptorError(
                        "The App store does not have a version '%s' of Core!"
                        % self._version
                    )
            else:
                # engines, apps etc have a 'bundle level entity' in the app store,
                # e.g. something representing the app or engine.
                # then a version entity representing a particular version
                sg_bundle_data = sg.find_one(
                    bundle_entity_type,
                    [["sg_system_name", "is", self._name]],
                    self._BUNDLE_FIELDS_TO_CACHE,
                )

                if sg_bundle_data is None:
                    raise TankDescriptorError(
                        "The App store does not contain an item named '%s'!"
                        % self._name
                    )

                # now get the version
                sg_version_data = sg.find_one(
                    version_entity_type,
                    [[link_field, "is", sg_bundle_data], ["code", "is", self._version]],
                    self._VERSION_FIELDS_TO_CACHE,
                )
                if sg_version_data is None:
                    raise TankDescriptorError(
                        "The App store does not have a "
                        "version '%s' of item '%s'!" % (self._version, self._name)
                    )

        # create metadata
        metadata = {
            "sg_bundle_data": sg_bundle_data,
            "sg_version_data": sg_version_data,
        }

        # try to write to location - but it may be located in a
        # readonly bundle cache - if the caching fails, gracefully
        # fall back and log
        try:
            fp = open(cache_file, "wb")
            try:
                pickle.dump(metadata, fp)
                log.debug("Wrote app store metadata cache '%s'" % cache_file)
            finally:
                fp.close()
        except Exception as e:
            log.debug(
                "Did not update app store metadata cache '%s': %s" % (cache_file, e)
            )

        return metadata

    def _get_bundle_cache_path(self, bundle_cache_root):
        """
        Given a cache root, compute a cache path suitable
        for this descriptor, using the 0.18+ path format.

        :param bundle_cache_root: Bundle cache root path
        :return: Path to bundle cache location
        """
        return os.path.join(
            bundle_cache_root, "app_store", self.get_system_name(), self.get_version()
        )

    def _get_cache_paths(self):
        """
        Get a list of resolved paths, starting with the primary and
        continuing with alternative locations where it may reside.

        Note: This method only computes paths and does not perform any I/O ops.

        :return: List of path strings
        """
        # get default cache paths from base class
        paths = super(IODescriptorAppStore, self)._get_cache_paths()

        # for compatibility with older versions of core, prior to v0.18.x,
        # add the old-style bundle cache path as a fallback. As of v0.18.x,
        # the bundle cache subdirectory names were shortened and otherwise
        # modified to help prevent MAX_PATH issues on windows. This call adds
        # the old path as a fallback for cases where core has been upgraded
        # for an existing project. NOTE: This only works because the bundle
        # cache root didn't change (when use_bundle_cache is set to False).
        # If the bundle cache root changes across core versions, then this will
        # need to be refactored.
        legacy_folder = self._get_legacy_bundle_install_folder(
            "app_store",
            self._bundle_cache_root,
            self._bundle_type,
            self.get_system_name(),
            self.get_version(),
        )
        if legacy_folder:
            paths.append(legacy_folder)

        return paths

    ###############################################################################################
    # data accessors

    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk
        """
        return self._name

    def get_deprecation_status(self):
        """
        Returns information about deprecation.

        May download the item from the app store in order
        to retrieve the metadata.

        :returns: Returns a tuple (is_deprecated, message) to indicate
                  if this item is deprecated.
        """
        # make sure we have the app payload + metadata
        self.ensure_local()
        # grab metadata
        metadata = self.__load_cached_app_store_metadata(self.get_path())
        sg_bundle_data = metadata.get("sg_bundle_data") or {}
        if sg_bundle_data.get("sg_status_list") == "dep":
            msg = sg_bundle_data.get("sg_deprecation_message", "No reason given.")
            return (True, msg)
        else:
            return (False, "")

    def get_version(self):
        """
        Returns the version number string for this item
        """
        return self._version

    def get_changelog(self):
        """
        Returns information about the changelog for this item.

        May download the item from the app store in order
        to retrieve the metadata.

        :returns: A tuple (changelog_summary, changelog_url). Values may be None
                  to indicate that no changelog exists.
        """
        summary = None
        url = None

        # make sure we have the app payload + metadata
        self.ensure_local()
        # grab metadata
        metadata = self.__load_cached_app_store_metadata(self.get_path())
        try:
            sg_version_data = metadata.get("sg_version_data") or {}
            summary = sg_version_data.get("description")
            url = sg_version_data.get("sg_detailed_release_notes").get("url")
        except Exception:
            pass
        return (summary, url)

    def _download_local(self, destination_path):
        """
        Retrieves this version to local repo.

        :param destination_path: The directory to which the app store descriptor
        is to be downloaded to.
        """
        # connect to the app store
        (sg, script_user) = self.__create_sg_app_store_connection()

        # fetch metadata from sg...
        metadata = self.__refresh_metadata(destination_path)

        # now get the attachment info
        version = metadata.get("sg_version_data")

        # attachment field is on the following form in the case a file has been uploaded:
        #  {'name': 'v1.2.3.zip',
        #  'url': 'https://sg-media-usor-01.s3.amazonaws.com/...',
        #  'content_type': 'application/zip',
        #  'type': 'Attachment',
        #  'id': 139,
        #  'link_type': 'upload'}
        attachment_id = version[constants.TANK_CODE_PAYLOAD_FIELD]["id"]

        # download and unzip
        try:
            shotgun.download_and_unpack_attachment(sg, attachment_id, destination_path)
        except ShotgunAttachmentDownloadError as e:
            raise TankAppStoreError("Failed to download %s. Error: %s" % (self, e))

    def _post_download(self, download_path):
        """
        Code run after the descriptor is successfully downloaded to disk

        :param download_path: The path to which the descriptor is downloaded to.
        """
        # write a stats record to the tank app store
        try:
            # connect to the app store
            (sg, script_user) = self.__create_sg_app_store_connection()

            # fetch metadata from sg...
            metadata = self.__refresh_metadata(download_path)

            # now get the attachment info
            version = metadata.get("sg_version_data")

            # setup the data entry
            data = {}
            data["description"] = "%s: %s %s was downloaded" % (
                self._sg_connection.base_url,
                self._name,
                self._version,
            )
            data["event_type"] = self._DOWNLOAD_STATS_EVENT_TYPE[self._bundle_type]
            data["entity"] = version
            data["user"] = script_user
            data["project"] = constants.TANK_APP_STORE_DUMMY_PROJECT
            data["attribute_name"] = constants.TANK_CODE_PAYLOAD_FIELD

            # log the data to shotgun
            sg.create("EventLogEntry", data)
        except Exception as e:
            log.warning("Could not write app store download receipt: %s" % e)

    #############################################################################
    # searching for other versions

    def get_latest_cached_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version
        that is locally available in the bundle cache search path.

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: instance deriving from IODescriptorBase or None if not found
        """
        log.debug("Looking for cached versions of %r..." % self)
        all_versions = self._get_locally_cached_versions()
        log.debug("Found %d versions" % len(all_versions))

        if self._label:
            # now filter the list of versions to only include things with
            # the sought-after label
            version_numbers = []
            log.debug("culling out versions not labelled '%s'..." % self._label)
            for (version_str, path) in all_versions.items():
                metadata = self.__load_cached_app_store_metadata(path)
                try:
                    tags = [x["name"] for x in metadata["sg_version_data"]["tags"]]
                    if self.__match_label(tags):
                        version_numbers.append(version_str)
                except Exception as e:
                    log.debug(
                        "Could not determine label metadata for %s. Ignoring. Details: %s"
                        % (path, e)
                    )

        else:
            # no label based filtering. all versions are valid.
            version_numbers = list(all_versions.keys())

        if len(version_numbers) == 0:
            return None

        version_to_use = self._find_latest_tag_by_pattern(
            version_numbers, constraint_pattern
        )
        if version_to_use is None:
            return None

        # make a descriptor dict
        descriptor_dict = {
            "type": "app_store",
            "name": self._name,
            "version": version_to_use,
        }

        if self._label:
            descriptor_dict["label"] = self._label

        # and return a descriptor instance
        desc = IODescriptorAppStore(
            descriptor_dict, self._sg_connection, self._bundle_type
        )
        desc.set_cache_roots(self._bundle_cache_root, self._fallback_roots)

        log.debug("Latest cached version resolved to %r" % desc)
        return desc

    @LogManager.log_timing
    def get_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.

        This method will connect to the toolkit app store and download
        metadata to determine the latest version.

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: IODescriptorAppStore object
        """
        log.debug(
            "Determining latest version for %r given constraint pattern %s"
            % (self, constraint_pattern)
        )

        # connect to the app store
        (sg, _) = self.__create_sg_app_store_connection()

        # get latest get the filter logic for what to exclude
        if constants.APP_STORE_QA_MODE_ENV_VAR in os.environ:
            sg_filter = [["sg_status_list", "is_not", "bad"]]
        else:
            sg_filter = [
                ["sg_status_list", "is_not", "rev"],
                ["sg_status_list", "is_not", "bad"],
            ]

        if self._bundle_type != self.CORE:
            # find the main entry
            sg_bundle_data = sg.find_one(
                self._APP_STORE_OBJECT[self._bundle_type],
                [["sg_system_name", "is", self._name]],
                self._BUNDLE_FIELDS_TO_CACHE,
            )

            if sg_bundle_data is None:
                raise TankDescriptorError(
                    "App store does not contain an item named '%s'!" % self._name
                )

            # now get all versions
            link_field = self._APP_STORE_LINK[self._bundle_type]
            entity_type = self._APP_STORE_VERSION[self._bundle_type]
            sg_filter += [[link_field, "is", sg_bundle_data]]

        else:
            # core doesn't have a parent entity for its versions
            sg_bundle_data = None
            entity_type = constants.TANK_CORE_VERSION_ENTITY_TYPE

        # optimization: if there is no constraint pattern and no label
        # set, just download the latest record
        if self._label is None and constraint_pattern is None:
            # only download one record
            limit = 1
        else:
            limit = 0  # all records

        # now get all versions
        sg_versions = sg.find(
            entity_type,
            filters=sg_filter,
            fields=self._VERSION_FIELDS_TO_CACHE,
            order=[{"field_name": "created_at", "direction": "desc"}],
            limit=limit,
        )

        log.debug("Downloaded data for %d versions from Flow Production Tracking." % len(sg_versions))

        # now filter out all labels that aren't matching
        matching_records = []
        for sg_version_entry in sg_versions:
            tags = [x["name"] for x in sg_version_entry["tags"]]
            if self.__match_label(tags):
                matching_records.append(sg_version_entry)

        log.debug(
            "After applying label filters, %d records remain." % len(matching_records)
        )

        if len(matching_records) == 0:
            raise TankDescriptorError(
                "Cannot find any versions for %s in the App store!" % self
            )

        # and filter out based on version constraint
        if constraint_pattern:

            version_numbers = [x.get("code") for x in matching_records]
            version_to_use = self._find_latest_tag_by_pattern(
                version_numbers, constraint_pattern
            )
            if version_to_use is None:
                raise TankDescriptorError(
                    "'%s' does not have a version matching the pattern '%s'. "
                    "Available versions are: %s"
                    % (
                        self.get_system_name(),
                        constraint_pattern,
                        ", ".join(version_numbers),
                    )
                )
            # get the sg data for the given version
            sg_data_for_version = [
                d for d in matching_records if d["code"] == version_to_use
            ][0]

        else:
            # no constraints applied. Pick first (latest) match
            sg_data_for_version = matching_records[0]
            version_to_use = sg_data_for_version["code"]

        # make a descriptor dict
        descriptor_dict = {
            "type": "app_store",
            "name": self._name,
            "version": version_to_use,
        }

        if self._label:
            descriptor_dict["label"] = self._label

        # and return a descriptor instance
        desc = IODescriptorAppStore(
            descriptor_dict, self._sg_connection, self._bundle_type
        )
        desc.set_cache_roots(self._bundle_cache_root, self._fallback_roots)

        # if this item exists locally, attempt to update the metadata cache
        # this ensures that if labels are added in the app store, these
        # are correctly cached locally.
        cached_path = desc.get_path()
        if cached_path:
            desc.__refresh_metadata(cached_path, sg_bundle_data, sg_data_for_version)

        return desc

    def __match_label(self, tag_list):
        """
        Given a list of tags, see if it matches the given label

        Shotgun tags are glob style: *, 2017.*, 2018.2

        :param tag_list: list of tags (strings) from shotgun
        :return: True if matching false if not
        """
        if self._label is None:
            # no label set - all matching!
            return True

        if tag_list is None:
            # no tags defined, so no match
            return False

        # glob match each item
        for tag in tag_list:
            if fnmatch.fnmatch(self._label, tag):
                return True

        return False

    @LogManager.log_timing
    def __create_sg_app_store_connection(self):
        """
        Creates a shotgun connection that can be used to access the Toolkit app store.

        :returns: (sg, dict) where the first item is the shotgun api instance and the second
                  is an sg entity dictionary (keys type/id) corresponding to to the user used
                  to connect to the app store.
        """
        # maintain a cache for performance
        # cache is keyed by client shotgun site
        # this assumes that there is a strict
        # 1:1 relationship between app store accounts
        # and shotgun sites.

        if os.environ.get(constants.DISABLE_APPSTORE_ACCESS_ENV_VAR, "0") == "1":
            message = (
                "The '%s' environment variable is active, preventing connection to app store."
                % constants.DISABLE_APPSTORE_ACCESS_ENV_VAR
            )
            log.debug(message)
            raise TankAppStoreConnectionError(message)

        sg_url = self._sg_connection.base_url

        if sg_url not in self._app_store_connections:

            # Connect to associated Shotgun site and retrieve the credentials to use to
            # connect to the app store site
            try:
                (script_name, script_key) = self.__get_app_store_key_from_shotgun()
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    # edge case alert!
                    # this is likely because our session token in shotgun has expired.
                    # The authentication system is based around wrapping the shotgun API,
                    # and requesting authentication if needed. Because the app store
                    # credentials is a separate endpoint and doesn't go via the shotgun
                    # API, we have to explicitly check.
                    #
                    # trigger a refresh of our session token by issuing a shotgun API call
                    self._sg_connection.find_one("HumanUser", [])
                    # and retry
                    (script_name, script_key) = self.__get_app_store_key_from_shotgun()
                else:
                    raise

            app_store = os.environ.get("SGTK_APP_STORE", constants.SGTK_APP_STORE)

            log.debug("Connecting to %s..." % app_store)
            # Connect to the app store and resolve the script user id we are connecting with.
            # Set the timeout explicitly so we ensure the connection won't hang in cases where
            # a response is not returned in a reasonable amount of time.
            app_store_sg = shotgun_api3.Shotgun(
                app_store,
                script_name=script_name,
                api_key=script_key,
                http_proxy=self.__get_app_store_proxy_setting(),
                connect=False,
            )
            # set the default timeout for app store connections
            app_store_sg.config.timeout_secs = constants.SGTK_APP_STORE_CONN_TIMEOUT

            # determine the script user running currently
            # get the API script user ID from shotgun
            try:
                script_user = app_store_sg.find_one(
                    "ApiUser",
                    filters=[["firstname", "is", script_name]],
                    fields=["type", "id"],
                )
            except shotgun_api3.AuthenticationFault:
                raise InvalidAppStoreCredentialsError(
                    "The Toolkit App Store credentials found in PTR are invalid.\n"
                    "Please contact support at %s to resolve this issue." % SUPPORT_URL
                )
            # Connection errors can occur for a variety of reasons. For example, there is no
            # internet access or there is a proxy server blocking access to the Toolkit app store.
            except (
                httplib2.HttpLib2Error,
                httplib2.socks.HTTPError,
                http_client.HTTPException,
            ) as e:
                raise TankAppStoreConnectionError(e)
            # In cases where there is a firewall/proxy blocking access to the app store, sometimes
            # the firewall will drop the connection instead of rejecting it. The API request will
            # timeout which unfortunately results in a generic SSLError with only the message text
            # to give us a clue why the request failed.
            # The exception raised in this case is "ssl.SSLError: The read operation timed out"
            except httplib2.ssl.SSLError as e:
                if "timed" in str(e):
                    raise TankAppStoreConnectionError(
                        "Connection to %s timed out: %s"
                        % (app_store_sg.config.server, e)
                    )
                else:
                    # other type of ssl error
                    raise TankAppStoreError(e)
            except Exception as e:
                raise TankAppStoreError(e)

            if script_user is None:
                raise TankAppStoreError(
                    "Could not evaluate the current App Store User! Please contact support."
                )

            self._app_store_connections[sg_url] = (app_store_sg, script_user)

        return self._app_store_connections[sg_url]

    def __get_app_store_proxy_setting(self):
        """
        Retrieve the app store proxy settings. If the key app_store_http_proxy is not found in the
        ``shotgun.yml`` file, the proxy settings from the client site connection will be used. If the
        key is found, than its value will be used. Note that if the ``app_store_http_proxy`` setting
        is set to ``null`` or an empty string in the configuration file, it means that the app store
        proxy is being forced to ``None`` and therefore won't be inherited from the http proxy setting.

        :returns: The http proxy connection string.
        """
        try:
            config_data = shotgun.get_associated_sg_config_data()
        except UnresolvableCoreConfigurationError:
            config_data = None

        if config_data and constants.APP_STORE_HTTP_PROXY in config_data:
            return config_data[constants.APP_STORE_HTTP_PROXY]

        settings = UserSettings()
        if settings.app_store_proxy is not None:
            return settings.app_store_proxy

        # Use the http proxy from the connection so we don't have to run
        # the connection hook again or look up the system settings as they
        # will have been previously looked up to create the connection to Shotgun.
        return self._sg_connection.config.raw_http_proxy

    @LogManager.log_timing
    def __get_app_store_key_from_shotgun(self):
        """
        Given a Shotgun url and script credentials, fetch the app store key
        for this shotgun instance using a special controller method.
        Returns a tuple with (app_store_script_name, app_store_auth_key)

        :returns: tuple of strings with contents (script_name, script_key)
        """
        sg = self._sg_connection

        log.debug("Retrieving app store credentials from %s" % sg.base_url)

        # handle proxy setup by pulling the proxy details from the main shotgun connection
        if sg.config.proxy_handler:
            opener = urllib.request.build_opener(sg.config.proxy_handler)
            urllib.request.install_opener(opener)

        # now connect to our site and use a special url to retrieve the app store script key
        session_token = sg.get_session_token()
        post_data = {"session_token": session_token}
        response = urllib.request.urlopen(
            "%s/api3/sgtk_install_script" % sg.base_url,
            six.ensure_binary(urllib.parse.urlencode(post_data)),
        )
        html = response.read()
        data = json.loads(html)

        if not data["script_name"] or not data["script_key"]:
            raise InvalidAppStoreCredentialsError(
                "Toolkit App Store credentials could not be retrieved from Flow Production Tracking.\n"
                "Please contact support at %s to resolve this issue." % SUPPORT_URL
            )

        log.debug(
            "Retrieved app store credentials for account '%s'." % data["script_name"]
        )

        return data["script_name"], data["script_key"]

    def has_remote_access(self):
        """
        Probes if the current descriptor is able to handle
        remote requests. If this method returns, true, operations
        such as :meth:`download_local` and :meth:`get_latest_version`
        can be expected to succeed.

        :return: True if a remote is accessible, false if not.
        """

        # check if we can connect to Shotgun
        can_connect = True
        try:
            log.debug(
                "%r: Probing if a connection to the App Store can be established..."
                % self
            )
            # connect to the app store
            (sg, _) = self.__create_sg_app_store_connection()
            log.debug("...connection established: %s" % sg)
        except Exception as e:
            log.debug("...could not establish connection: %s" % e)
            can_connect = False
        return can_connect
