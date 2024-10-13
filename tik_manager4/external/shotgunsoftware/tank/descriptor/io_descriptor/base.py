# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import contextlib

from .. import constants
from ... import LogManager
from ...util import filesystem, sgre as re
from ...util.version import is_version_newer
from ..errors import TankDescriptorError, TankMissingManifestError

from tank_vendor import yaml
from tank_vendor.six.moves import map, urllib

log = LogManager.get_logger(__name__)


class IODescriptorBase(object):
    """
    An I/O descriptor describes a particular version of an app, engine or core component.
    It also knows how to access metadata such as documentation, descriptions etc.

    Several Descriptor classes exists, all deriving from this base class, and the
    factory method create_descriptor() manufactures the correct descriptor object
    based on a descriptor dict, that is found inside of the environment config.

    Different App Descriptor implementations typically handle different source control
    systems: There may be an app descriptor which knows how to communicate with the
    Tank App store and one which knows how to handle the local file system.
    """

    _factory = {}

    @classmethod
    def register_descriptor_factory(cls, descriptor_type, subclass):
        """
        Registers a descriptor subclass with the :meth:`create` factory. This is
        necessary to remove local imports from IODescriptorBase subclasses to prevent
        problems during core swapping.

        :param descriptor_type: String type name of the descriptor, as will
            appear in the app location configuration.
        :param subclass: Class deriving from IODescriptorBase to associate.
        """
        cls._factory[descriptor_type] = subclass

    @classmethod
    def create(cls, bundle_type, descriptor_dict, sg_connection):
        """
        Factory method used by :meth:`create_descriptor`. This complex factory
        pattern is necessary to remove local imports from IODescriptorBase subclasses
        to prevent problems during core swapping.

        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        :param descriptor_dict: Descriptor dictionary describing the bundle.
        :param sg_connection: Shotgun connection to associated site.
        :returns: Instance of class deriving from :class:`IODescriptorBase`
        :raises: TankDescriptorError
        """
        descriptor_type = descriptor_dict.get("type")
        if descriptor_type not in cls._factory:
            raise TankDescriptorError(
                "Unknown descriptor type for '%s'" % descriptor_dict
            )
        class_obj = cls._factory[descriptor_type]
        return class_obj(descriptor_dict, sg_connection, bundle_type)

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: Dictionary describing what
                                the descriptor is pointing at.
        :param sg_connection: Shotgun connection to associated site.
        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        """
        self._bundle_cache_root = None
        self._fallback_roots = []
        self._descriptor_dict = descriptor_dict
        self.__manifest_data = None
        self._is_copiable = True

    def set_cache_roots(self, primary_root, fallback_roots):
        """
        Specify where to go look for cached versions of the app.
        The primary root is where new data is always written to
        if something is downloaded and cached. The fallback_roots
        parameter is a list of paths where the descriptor system
        will look in case a cached entry is not found in the
        primary root. If you specify several fallback roots, they
        will be traversed in order.

        This is an internal method that is part of the construction
        of the descriptor instances. Do not call directly.

        :param primary_root: Path for reading and writing cached apps
        :param fallback_roots: Paths to attempt to read cached apps from
                               in case it's not found in the primary root.
                               Paths will be traversed in the order they are
                               specified.

        """
        self._bundle_cache_root = primary_root
        self._fallback_roots = fallback_roots

    def __str__(self):
        """
        Human readable representation
        """
        # fall back onto uri which is semi-human-readable
        # it is recommended that each class implements its own
        # operator in order to better customize the ux.
        return self.get_uri()

    def __repr__(self):
        """
        Low level representation
        """
        class_name = self.__class__.__name__
        return "<%s %s>" % (class_name, self.get_uri())

    @classmethod
    def _validate_descriptor(cls, descriptor_dict, required, optional):
        """
        Validate that the descriptor dictionary has got the necessary keys.

        Raises TankDescriptorError if required parameters are missing.
        Logs warnings if parameters outside the required/optional range are specified.

        :param descriptor_dict: descriptor dict
        :param required: List of required parameters
        :param optional: List of optionally supported parameters
        :raises: TankDescriptorError if the descriptor dict does not include all parameters.
        """
        desc_keys_set = set(descriptor_dict.keys())
        required_set = set(required)
        # Add deny_platforms and disabled to the list of optional parameters as these are globally supported across
        # all descriptors and are used by the environment code to check if an item is disabled.
        optional_set = set(optional + ["deny_platforms", "disabled"])

        if not required_set.issubset(desc_keys_set):
            missing_keys = required_set.difference(desc_keys_set)
            raise TankDescriptorError(
                "%s are missing required keys %s" % (descriptor_dict, missing_keys)
            )

        all_keys = required_set.union(optional_set)

        if desc_keys_set.difference(all_keys):
            log.warning(
                "Found unsupported parameters %s in %s. "
                "These will be ignored."
                % (desc_keys_set.difference(all_keys), descriptor_dict)
            )

    @classmethod
    def _get_legacy_bundle_install_folder(
        cls,
        descriptor_name,
        install_cache_root,
        bundle_type,
        bundle_name,
        bundle_version,
    ):
        """Return the path to the legacy bundle install dir for the supplied info.

        :param descriptor_name: The name of the descriptor. ex: "app_store" or "git"
        :param install_cache_root: The root path to the bundle cache.
        :param bundle_type: The type of the bundle. Should be one of:
            Descriptor.APP, Descriptor.ENGINE, or Descriptor.FRAMEWORK.
        :param bundle_name: The display name for the resolved descriptor resource.
            ex: "tk-multi-shotgunpanel"
        :param bundle_version: The version of the bundle on disk. ex: "v1.2.5"
        :rtype: str
        :return: The path to the cache in the legacy bundle structure. None
                 if the bundle type is not supported by the 0.17 legacy structure.

        This method is provided for compatibility with older versions of core,
        prior to v0.18.x. As of v0.18.x, the bundle cache subdirectory names
        were shortened and otherwise modified to help prevent MAX_PATH issues
        on windows. This method is used to add the old style path as a fallback
        for cases like core having been upgraded to v0.18.x on an existing project.

        New style cache path:
            <root>/app_store/tk-multi-shotgunpanel/v1.2.5

        Legacy style cache path:
            <root>/apps/app_store/tk-multi-shotgunpanel/v1.2.5

        For reference, this method emulates: `tank.deploy.descriptor._get_local_location`
        in the pre-v0.18.x core.

        """
        from ..descriptor import Descriptor

        if bundle_type == Descriptor.APP:
            legacy_dir = "apps"
        elif bundle_type == Descriptor.ENGINE:
            legacy_dir = "engines"
        elif bundle_type == Descriptor.FRAMEWORK:
            legacy_dir = "frameworks"
        else:
            # 0.17 structure does not support any other
            # bundle types
            return None

        # build and return the path.
        # example: <root>/apps/app_store/tk-multi-shotgunpanel/v1.2.5
        return os.path.join(
            install_cache_root, legacy_dir, descriptor_name, bundle_name, bundle_version
        )

    def _find_latest_tag_by_pattern(self, version_numbers, pattern):
        """
        Given a list of version strings (e.g. 'v1.2.3'), find the one
        that best matches the given pattern.

        Version numbers passed in that don't match the pattern v1.2.3... will be ignored.

        If pattern is None, the highest version number is returned.

        :param version_numbers: List of version number strings, e.g. ``['v1.2.3', 'v1.2.5']``
        :param pattern: Version pattern string, e.g. 'v1.x.x'. Patterns are on the following forms:

            - v1.2.3 (can return this v1.2.3 but also any forked version under, eg. v1.2.3.2)
            - v1.2.x (examples: v1.2.4, or a forked version v1.2.4.2)
            - v1.x.x (examples: v1.3.2, a forked version v1.3.2.2)
            - v1.2.3.x (will always return a forked version, eg. v1.2.3.2)
            - None (latest version is returned)

        :returns: The most appropriate tag in the given list of tags or None if no tag matches
        :raises: TankDescriptorError if parsing fails
        """
        if len(version_numbers) == 0:
            return None

        # first handle case where pattern is None
        if pattern is None:
            # iterate over versions in list and find latest
            latest_version = None
            for version_number in version_numbers:
                if is_version_newer(version_number, latest_version):
                    latest_version = version_number
            return latest_version

        # now put all version number strings which match the form
        # vX.Y.Z(.*) into a nested dictionary where it is keyed recursively
        # by each digit (ie. major, minor, increment, then any additional
        # digit optionally used by forked versions)
        #
        versions = {}
        for version_num in version_numbers:
            try:
                version_split = list(map(int, version_num[1:].split(".")))
            except Exception:
                # this git tag is not on the expected form vX.Y.Z where X Y and Z are ints. skip.
                continue

            if len(version_split) < 3:
                # git tag has no minor or increment number. skip.
                continue

            # fill our versions dictionary
            #
            # For example, the following versions:
            # v1.2.1, v1.2.2, v1.2.3.1, v1.4.3, v1.4.2.1, v1.4.2.2, v1.4.1,
            #
            # Would generate the following:
            # {1:
            #   {2: {1: {},
            #        2: {},
            #        3: {1: {}
            #       }
            #   },
            #   4: {1: {},
            #       2: {1: {}, 2: {}},
            #       3: {}
            #       }
            #   }
            # }
            #
            current = versions
            for number in version_split:
                if number not in current:
                    current[number] = {}
                current = current[number]

        # now search for the latest version matching our pattern
        if not re.match("^v([0-9]+|x)(.([0-9]+|x)){2,}$", pattern):
            raise TankDescriptorError("Cannot parse version expression '%s'!" % pattern)

        # split our pattern, beware each part is a string (even integers)
        version_split = re.findall("([0-9]+|x)", pattern)
        if "x" in version_split:
            # check that we don't have an incorrect pattern using x
            # then a digit, eg. v4.x.2
            if re.match(r"^v[0-9\.]+[x\.]+[0-9\.]+$", pattern):
                raise TankDescriptorError(
                    "Incorrect version pattern '%s'. "
                    "There should be no digit after a 'x'." % pattern
                )

        current = versions
        version_to_use = None
        # process each digit in the pattern
        for version_digit in version_split:
            if version_digit == "x":
                # replace the 'x' by the latest at this level
                version_digit = max(list(current.keys()), key=int)
            version_digit = int(version_digit)
            if version_digit not in current:
                # no matches
                return None
            current = current[version_digit]
            if version_to_use is None:
                version_to_use = "v%d" % version_digit
            else:
                version_to_use = version_to_use + ".%d" % version_digit

        # at this point we have a matching version (eg. v4.x.x => v4.0.2) but
        # there may be forked versions under this 4.0.2, so continue to recurse into
        # the versions dictionary to find the latest forked version
        while len(current):
            version_digit = max(current.keys())
            current = current[version_digit]
            version_to_use = version_to_use + ".%d" % version_digit

        return version_to_use

    def _get_locally_cached_versions(self):
        """
        Given all cache locations, try to establish a list of versions
        available on disk.

        note that this logic is not applicable to all descriptor types,
        one ones which are listing all its versions as subfolders under
        a root location.

        :return: dictionary of bundle paths, keyed by version string
        """
        all_versions = {}
        for possible_cache_path in self._get_cache_paths():
            # get the parent folder for the current version path
            parent_folder = os.path.dirname(possible_cache_path)
            # now look for child folders here - these are all the
            # versions stored in this cache area
            log.debug("Scanning for versions in '%s'" % parent_folder)
            if os.path.exists(parent_folder):
                for version_folder in os.listdir(parent_folder):
                    version_full_path = os.path.join(parent_folder, version_folder)
                    # check that it's a folder and not a system folder
                    if (
                        os.path.isdir(version_full_path)
                        and not version_folder.startswith("_")
                        and not version_folder.startswith(".")
                        and self._exists_local(version_full_path)
                    ):
                        # looks like a valid descriptor. Make sure
                        # it is valid and fully downloaded
                        all_versions[version_folder] = version_full_path

        return all_versions

    def set_is_copiable(self, copiable):
        """
        Sets whether copying is supported by this descriptor.

        :param bool copiable: If True, bundle can be copied.
        """
        self._is_copiable = copiable

    def copy(self, target_path, skip_list=None):
        """
        Copy the contents of the descriptor to an external location, if supported.

        :param target_path: target path to copy the descriptor to.
        :param skip_list: List of folders or files that should not be copied into the destination.

        .. note::
            The folders or files specified must be at the root of the bundle.
        """
        if self._is_copiable:
            self._copy(target_path, skip_list)
        else:
            raise TankDescriptorError("%r cannot be copied." % self)

    def _copy(self, target_path, skip_list=None):
        """
        Copy the contents of the descriptor to an external location, if supported.

        :param target_path: target path to copy the descriptor to.
        :param skip_list: List of folders or files that should not be copied into the destination.

        .. note::
            The folders or files specified must be at the root of the bundle.
        """
        log.debug("Copying %r -> %s" % (self, target_path))
        # base class implementation does a straight copy
        # make sure config exists
        self.ensure_local()
        # copy descriptor in
        filesystem.copy_folder(
            self.get_path(),
            target_path,
            skip_list=(skip_list or []) + filesystem.SKIP_LIST_DEFAULT,
        )

    def get_manifest(self, file_location):
        """
        Returns the info.yml metadata associated with this descriptor.
        Note that this call involves deep introspection; in order to
        access the metadata we normally need to have the code content
        local, so this method may trigger a remote code fetch if necessary.

        :param file_location: Path relative to the root of the bundle where info.yml
            can be found.

        :returns: dictionary with the contents of info.yml
        """
        if self.__manifest_data is None:
            # make sure payload exists locally
            if not self.exists_local():
                # @todo - at this point add to a metadata cache for performance
                # we can either just store it in a pickle, in order to avoid yaml parsing, which
                # is expensive, or if we want to be more fancy, we can maintain a single
                # "registry" file which holds the metadata for all known bundles in a single place.
                # given that all descriptors are immutable (except the ones where the immutable)
                # property returns false, we can keep adding to this global cache file over time.
                self.download_local()

            # get the metadata

            bundle_root = self.get_path()
            file_path = os.path.join(bundle_root, file_location)

            if not os.path.exists(file_path):
                # at this point we have downloaded the bundle, but it may have
                # an invalid internal structure.
                raise TankMissingManifestError(
                    "Toolkit metadata file '%s' missing." % file_path
                )

            try:
                file_data = open(file_path)
                try:
                    metadata = yaml.load(file_data, Loader=yaml.FullLoader)
                finally:
                    file_data.close()
            except Exception as exp:
                raise TankDescriptorError(
                    "Cannot load metadata file '%s'. Error: %s" % (file_path, exp)
                )

            # cache it
            self.__manifest_data = metadata

        return self.__manifest_data

    @classmethod
    def dict_from_uri(cls, uri):
        """
        Convert a uri string into a descriptor dictionary.

        Example:

        - uri:           sgtk:descriptor:app_store?name=hello&version=v123
        - expected_type: app_store
        - returns:   {'type': 'app_store',
                      'name': 'hello',
                      'version': 'v123'}

        :param uri: uri string
        :return: dictionary with keys type and all keys specified
                 in the item_keys parameter matched up by items in the
                 uri string.
        """
        parsed_uri = urllib.parse.urlparse(uri)

        # example:
        #
        # >>> urlparse.urlparse("sgtk:descriptor:app_store?foo=bar&baz=buz")
        #
        # ParseResult(scheme='sgtk', netloc='', path='descriptor:app_store',
        #             params='', query='foo=bar&baz=buz', fragment='')
        #
        #
        # NOTE - it seems on some versions of python the result is different.
        #        this includes python2.5 but seems to affect other SKUs as well.
        #
        # uri: sgtk:descriptor:app_store?version=v0.1.2&name=tk-bundle
        #
        # python 2.6+ expected: ParseResult(
        # scheme='sgtk',
        # netloc='',
        # path='descriptor:app_store',
        # params='',
        # query='version=v0.1.2&name=tk-bundle',
        # fragment='')
        #
        # python 2.5 and others: (
        # 'sgtk',
        # '',
        # 'descriptor:app_store?version=v0.1.2&name=tk-bundle',
        # '',
        # '',
        # '')

        if parsed_uri.scheme != constants.DESCRIPTOR_URI_PATH_SCHEME:
            raise TankDescriptorError("Invalid uri '%s' - must begin with 'sgtk'" % uri)

        if parsed_uri.query == "":
            # in python 2.5 and others, the querystring is part of the path (see above)
            (path, query) = parsed_uri.path.split("?")
        else:
            path = parsed_uri.path
            query = parsed_uri.query

        split_path = path.split(constants.DESCRIPTOR_URI_SEPARATOR)
        # e.g. 'descriptor:app_store' -> ('descriptor', 'app_store')
        if (
            len(split_path) != 2
            or split_path[0] != constants.DESCRIPTOR_URI_PATH_PREFIX
        ):
            raise TankDescriptorError(
                "Invalid uri '%s' - must begin with sgtk:descriptor" % uri
            )

        descriptor_dict = {}

        descriptor_dict["type"] = split_path[1]

        # now pop remaining keys into a dict and key by item_keys
        for (param, value) in urllib.parse.parse_qs(query).items():
            if len(value) > 1:
                raise TankDescriptorError(
                    "Invalid uri '%s' - duplicate parameters" % uri
                )
            descriptor_dict[param] = value[0]

        return descriptor_dict

    def get_dict(self):
        """
        Returns the dictionary associated with this descriptor
        """
        return self._descriptor_dict

    @classmethod
    def uri_from_dict(cls, descriptor_dict):
        """
        Create a descriptor uri given some data

        {'type': 'app_store', 'bar':'baz'} --> 'sgtk:descriptor:app_store?bar=baz'

        :param descriptor_dict: descriptor dictionary
        :return: descriptor uri
        """
        if "type" not in descriptor_dict:
            raise TankDescriptorError(
                "Cannot create uri from %s - missing type field" % descriptor_dict
            )

        uri_chunks = [
            constants.DESCRIPTOR_URI_PATH_SCHEME,
            constants.DESCRIPTOR_URI_PATH_PREFIX,
            descriptor_dict["type"],
        ]
        uri = constants.DESCRIPTOR_URI_SEPARATOR.join(uri_chunks)

        qs_chunks = []
        # Sort keys so that the uri is the same across invocations. This is very important
        # because tests may start failing with different implementations of Python (like pypy)
        # or code using this value as a key in a dict.
        for param in sorted(descriptor_dict):
            if param == "type":
                continue

            # note: for readability of windows and git paths, do not convert '/@:\'
            quoted_value = urllib.parse.quote(str(descriptor_dict[param]), safe="@/:\\")
            qs_chunks.append("%s=%s" % (param, quoted_value))

        qs = "&".join(qs_chunks)

        return "%s?%s" % (uri, qs)

    def get_uri(self):
        """
        Return the string based uri representation of this object

        :return: Uri string
        """
        return self.uri_from_dict(self._descriptor_dict)

    def get_deprecation_status(self):
        """
        Returns information about deprecation.

        :returns: Returns a tuple (is_deprecated, message) to indicate
                  if this item is deprecated.
        """
        # only some descriptors handle this. Default is to not support deprecation, e.g.
        # always return that things are active.
        return False, ""

    def get_changelog(self):
        """
        Returns information about the changelog for this item.

        :returns: A tuple (changelog_summary, changelog_url). Values may be None
                  to indicate that no changelog exists.
        """
        return (None, None)

    def is_dev(self):
        """
        Returns true if this item is intended for development purposes
        """
        return False

    def is_immutable(self):
        """
        Returns true if this item's content never changes
        """
        return True

    def ensure_local(self):
        """
        Convenience method. Ensures that the descriptor exists locally.
        """
        if not self.exists_local():
            log.debug("Downloading %s to the local Toolkit install location..." % self)
            self.download_local()

    def exists_local(self):
        """
        Returns true if this item exists in a locally accessible form
        """
        return self.get_path() is not None

    def _exists_local(self, path):
        """
        Returns true if the given bundle path exists in valid local cached form

        This can be reimplemented in derived classes to have more complex validation,
        like ensuring that the bundle is fully downloaded.
        """
        if path is None:
            return False

        # check that the main path exists locally and is a folder
        if not os.path.isdir(path):
            return False

        return True

    def _get_primary_cache_path(self):
        """
        Get the path to the cache location in the bundle cache.

        This is the location where new app content should be
        downloaded to. This path is always returned as part
        of :meth:`_get_cache_paths`.

        .. note:: This method only computes paths and does not perform any I/O ops.

        :return: Path to the bundle cache location for this item.
        """
        return self._get_bundle_cache_path(self._bundle_cache_root)

    def _get_cache_paths(self):
        """
        Get a list of resolved paths, starting with the fallback roots
        in order and finishing with the bundle cache location.

        .. note:: This method only computes paths and does not perform any I/O ops.

        :return: List of path strings
        """
        paths = [self._get_bundle_cache_path(x) for x in self._fallback_roots]
        paths.append(self._get_primary_cache_path())
        return paths

    def get_path(self):
        """
        Returns the path to the folder where this item resides. If no
        cache exists for this path, None is returned.
        """
        for path in self._get_cache_paths():
            # we determine local existence based on the existence of the
            # bundle's directory on disk.
            if self._exists_local(path):
                return path

        return None

    def clone_cache(self, cache_root):
        """
        The descriptor system maintains an internal cache where it downloads
        the payload that is associated with the descriptor. Toolkit supports
        complex cache setups, where you can specify a series of path where toolkit
        should go and look for cached items.

        This is an advanced method that helps in cases where a user wishes to
        administer such a setup, allowing a cached payload to be copied from
        its current location into a new cache structure.

        If the cache already exists in the target location, nothing will happen.

        If the descriptor's payload doesn't exist on disk, it will be downloaded.

        :param cache_root: Root point of the cache location to copy to.
        :returns: True if the cache was copied, false if not
        """
        # compute new location
        new_cache_path = self._get_bundle_cache_path(cache_root)
        log.debug("Clone cache for %r: Copying to '%s'" % (self, new_cache_path))

        # like in get_path(), we determine local existence based on the info.yml
        info_yml_path = os.path.join(new_cache_path, constants.BUNDLE_METADATA_FILE)
        if os.path.exists(info_yml_path):
            # we already have a cache
            log.debug(
                "Bundle cache already exists in '%s'. Nothing to do." % new_cache_path
            )
            return False

        # make sure we have something to copy
        self.ensure_local()

        # check that we aren't trying to copy onto ourself
        if new_cache_path == self.get_path():
            log.debug(
                "Clone cache for %r: No need to copy, source and target are same."
                % self
            )
            return False

        # Cache the source cache path because we're about to create the destination folder,
        # which might be a bundle cache root.
        source_cache_path = self.get_path()
        log.debug("Source cache is located at %s", source_cache_path)

        # Cache the source cache path because we're about to create the destination folder,
        # which might be a bundle cache root.
        source_cache_path = self.get_path()
        log.debug("Source cache is located at %s", source_cache_path)

        # and to the actual I/O
        # pass an empty skip list to ensure we copy things like the .git folder
        filesystem.ensure_folder_exists(new_cache_path, permissions=0o777)
        filesystem.copy_folder(source_cache_path, new_cache_path, skip_list=[])
        return True

    ###############################################################################################
    # implemented by deriving classes

    def _get_bundle_cache_path(self, bundle_cache_root):
        """
        Given a cache root, compute a cache path suitable
        for this descriptor, using the 0.18+ path format.

        :param bundle_cache_root: Bundle cache root path
        :return: Path to bundle cache location
        """
        raise NotImplementedError

    @contextlib.contextmanager
    def open_write_location(self):
        """
        When used with the ``with`` statement, this context manager will yield the
        destination where a bundle should be downloaded. If the context is not exited successfully,
        the files will be removed from disk.

        :returns: Path to where the package should be extracted to.
        """
        raise TankDescriptorError(
            "open_write_location is not supported on the '%s' descriptor type."
            % self.get_dict()["type"]
        )

    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk, e.g. 'tk-maya'
        """
        raise NotImplementedError

    def get_version(self):
        """
        Returns the version number string for this item, .e.g 'v1.2.3'
        """
        raise NotImplementedError

    def download_local(self):
        """
        Retrieves this version to local repo.
        """
        pass

    def get_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: instance deriving from IODescriptorBase
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def has_remote_access(self):
        """
        Probes if the current descriptor is able to handle
        remote requests. If this method returns, true, operations
        such as :meth:`download_local` and :meth:`get_latest_version`
        can be expected to succeed.

        :return: True if a remote is accessible, false if not.
        """
        raise NotImplementedError
