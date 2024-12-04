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
import copy

from ..log import LogManager
from ..util import filesystem
from .io_descriptor import create_io_descriptor
from .errors import TankDescriptorError
from ..util import LocalFileStorageManager
from . import constants


logger = LogManager.get_logger(__name__)


def create_descriptor(
    sg_connection,
    descriptor_type,
    dict_or_uri,
    bundle_cache_root_override=None,
    fallback_roots=None,
    resolve_latest=False,
    constraint_pattern=None,
    local_fallback_when_disconnected=True,
):
    """
    Factory method. Use this when creating descriptor objects.

    .. note:: Descriptors inherit their threading characteristics from
        the shotgun connection that they carry internally. They are reentrant
        and should not be passed between threads.

    :param sg_connection: Shotgun connection to associated site
    :param descriptor_type: Either ``Descriptor.APP``, ``CORE``, ``CONFIG``, ``INSTALLED_CONFIG``,
        ``ENGINE`` or ``FRAMEWORK``
    :param dict_or_uri: A std descriptor dictionary dictionary or string
    :param bundle_cache_root_override: Optional override for root path to where
                                       downloaded apps are cached. If not specified,
                                       the global bundle cache location will be used. This location is a per-user
                                       cache that is shared across all sites and projects.
    :param fallback_roots: Optional List of immutable fallback cache locations where
                           apps will be searched for. Note that when descriptors
                           download new content, it always ends up in the
                           bundle_cache_root.
    :param resolve_latest: If true, the latest version will be determined and returned.

                           If set to True, no version information needs to be supplied with
                           the descriptor dictionary/uri for descriptor types which support
                           a version number concept. Please note that setting this flag
                           to true will typically affect performance - an external connection
                           is often required in order to establish what the latest version is.

                           If a remote connection cannot be established when attempting to determine
                           the latest version, a local scan will be carried out and the highest
                           version number that is cached locally will be returned.
    :param constraint_pattern: If resolve_latest is True, this pattern can be used to constrain
                           the search for latest to only take part over a subset of versions.
                           This is a string that can be on the following form:

                                - ``v0.1.2``, ``v0.12.3.2``, ``v0.1.3beta`` - a specific version
                                - ``v0.12.x`` - get the highest v0.12 version
                                - ``v1.x.x`` - get the highest v1 version
    :param local_fallback_when_disconnected: If resolve_latest is set to True, specify the behaviour
                            in the case when no connection to a remote descriptor can be established,
                            for example because and internet connection isn't available. If True, the
                            descriptor factory will attempt to fall back on any existing locally cached
                            bundles and return the latest one available. If False, a
                            :class:`TankDescriptorError` is raised instead.

    :returns: :class:`Descriptor` object
    :raises: :class:`TankDescriptorError`
    """
    # use the environment variable if set - if not, fall back on the override or default locations
    if os.environ.get(constants.BUNDLE_CACHE_PATH_ENV_VAR):
        bundle_cache_root_override = os.path.expanduser(
            os.path.expandvars(os.environ.get(constants.BUNDLE_CACHE_PATH_ENV_VAR))
        )
    elif bundle_cache_root_override is None:
        bundle_cache_root_override = _get_default_bundle_cache_root()
        filesystem.ensure_folder_exists(bundle_cache_root_override)
    else:
        # expand environment variables
        bundle_cache_root_override = os.path.expanduser(
            os.path.expandvars(bundle_cache_root_override)
        )

    fallback_roots = fallback_roots or []

    # expand environment variables
    fallback_roots = [os.path.expandvars(os.path.expanduser(x)) for x in fallback_roots]

    # first construct a low level IO descriptor
    io_descriptor = create_io_descriptor(
        sg_connection,
        descriptor_type,
        dict_or_uri,
        bundle_cache_root_override,
        fallback_roots,
        resolve_latest,
        constraint_pattern,
        local_fallback_when_disconnected,
    )

    # now create a high level descriptor and bind that with the low level descriptor
    return Descriptor.create(
        sg_connection,
        descriptor_type,
        io_descriptor,
        bundle_cache_root_override,
        fallback_roots,
    )


def _get_default_bundle_cache_root():
    """
    Returns the cache location for the default bundle cache.

    :returns: path on disk
    """
    return os.path.join(
        LocalFileStorageManager.get_global_root(LocalFileStorageManager.CACHE),
        "bundle_cache",
    )


class Descriptor(object):
    """
    A descriptor describes a particular version of an app, engine or core component.
    It also knows how to access metadata such as documentation, descriptions etc.

    Descriptor is subclassed to distinguish different types of payload;
    apps, engines, configs, cores etc. Each payload may have different accessors
    and helper methods.
    """

    APP = constants.DESCRIPTOR_APP
    FRAMEWORK = constants.DESCRIPTOR_FRAMEWORK
    ENGINE = constants.DESCRIPTOR_ENGINE
    CONFIG = constants.DESCRIPTOR_CONFIG
    CORE = constants.DESCRIPTOR_CORE
    INSTALLED_CONFIG = constants.DESCRIPTOR_INSTALLED_CONFIG

    _factory = {}

    @classmethod
    def register_descriptor_factory(cls, descriptor_type, subclass):
        """
        Registers a descriptor subclass with the :meth:`create` factory.
        This is an internal method that should not be called by external
        code.

        :param descriptor_type: Either ``Descriptor.APP``, ``CORE``,
            ``CONFIG``, ``INSTALLED_CONFIG``, ``ENGINE`` or ``FRAMEWORK``
        :param subclass: Class deriving from Descriptor to associate.
        """
        cls._factory[descriptor_type] = subclass

    @classmethod
    def create(
        cls,
        sg_connection,
        descriptor_type,
        io_descriptor,
        bundle_cache_root_override,
        fallback_roots,
    ):
        """
        Factory method used by :meth:`create_descriptor`. This is an internal
        method that should not be called by external code.

        :param descriptor_type: Either ``Descriptor.APP``, ``CORE``,
            ``CONFIG``, ``INSTALLED_CONFIG``, ``ENGINE`` or ``FRAMEWORK``
        :param sg_connection: Shotgun connection to associated site
        :param io_descriptor: Associated low level descriptor transport object.
        :param bundle_cache_root_override: Override for root path to where
            downloaded apps are cached.
        :param fallback_roots: List of immutable fallback cache locations where
            apps will be searched for.
        :returns: Instance of class deriving from :class:`Descriptor`
        :raises: TankDescriptorError
        """
        if descriptor_type not in cls._factory:
            raise TankDescriptorError(
                "Unsupported descriptor type %s" % descriptor_type
            )
        class_obj = cls._factory[descriptor_type]
        return class_obj(
            sg_connection, io_descriptor, bundle_cache_root_override, fallback_roots
        )

    def __init__(self, io_descriptor):
        """
        .. note:: Use the factory method :meth:`create_descriptor` when
                  creating new descriptor objects.

        :param io_descriptor: Associated IO descriptor.
        """
        # construct a suitable IO descriptor for this descriptor
        self._io_descriptor = io_descriptor

    def __eq__(self, other):
        # By default, we can assume equality if the path to the data
        # on disk is equivalent.
        if isinstance(other, self.__class__):
            return self.get_path() == other.get_path()
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        """
        Used for debug logging
        """
        class_name = self.__class__.__name__
        return "<%s %r>" % (class_name, self._io_descriptor)

    def __str__(self):
        """
        Used for pretty printing
        """
        return "%s %s" % (self.system_name, self.version)

    def _get_manifest(self):
        """
        Returns the info.yml metadata associated with this descriptor.

        :returns: dictionary with the contents of info.yml
        """
        return self._io_descriptor.get_manifest(constants.BUNDLE_METADATA_FILE)

    ###############################################################################################
    # data accessors

    def get_dict(self):
        """
        Returns the dictionary associated with this descriptor

        :returns: Dictionary that can be used to construct the descriptor
        """
        return self._io_descriptor.get_dict()

    # legacy support for previous method name
    get_location = get_dict

    def get_uri(self):
        """
        Returns the uri associated with this descriptor
        The uri is a string based representation that is equivalent to the
        descriptor dictionary returned by the get_dict() method.

        :returns: Uri string that can be used to construct the descriptor
        """
        return self._io_descriptor.get_uri()

    def copy(self, target_folder):
        """
        Copy the config descriptor into the specified target location.

        :param target_folder: Folder to copy the descriptor to
        """
        self._io_descriptor.copy(target_folder)

    def clone_cache(self, cache_root):
        """
        The descriptor system maintains an internal cache where it downloads
        the payload that is associated with the descriptor. Toolkit supports
        complex cache setups, where you can specify a series of path where toolkit
        should go and look for cached items.

        This is an advanced method that helps in cases where a user wishes to
        administer such a setup, allowing a cached payload to be copied from
        its current location into a new cache structure.

        If the descriptor's payload doesn't exist on disk, it will be downloaded.

        :param cache_root: Root point of the cache location to copy to.
        """
        return self._io_descriptor.clone_cache(cache_root)

    @property
    def display_name(self):
        """
        The display name for this item.
        If no display name has been defined, the system name will be returned.
        """
        meta = self._get_manifest()
        display_name = meta.get("display_name")
        if display_name is None:
            display_name = self.system_name
        return display_name

    def is_dev(self):
        """
        Returns true if this item is intended for development purposes

        :returns: True if this is a developer item
        """
        return self._io_descriptor.is_dev()

    def is_immutable(self):
        """
        Returns true if this descriptor never changes its content.
        This is true for most descriptors as they represent a particular
        version, tag or commit of an item. Examples of non-immutable
        descriptors include path and dev descriptors, where the
        descriptor points at a "live" location on disk where a user
        can make changes at any time.

        :returns: True if this is a developer item
        """
        return self._io_descriptor.is_immutable()

    @property
    def description(self):
        """
        A short description of the item.
        """
        meta = self._get_manifest()
        desc = meta.get("description")
        if desc is None:
            desc = "No description available."
        return desc

    @property
    def icon_256(self):
        """
        The path to a 256px square png icon file representing this item
        """
        app_icon = os.path.join(self._io_descriptor.get_path(), "icon_256.png")
        if os.path.exists(app_icon):
            return app_icon
        else:
            # return default
            default_icon = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), "resources", "default_bundle_256px.png"
                )
            )
            return default_icon

    @property
    def support_url(self):
        """
        A url that points at a support web page associated with this item.
        If not url has been defined, ``None`` is returned.
        """
        meta = self._get_manifest()
        support_url = meta.get("support_url")
        if support_url is None:
            support_url = "https://knowledge.autodesk.com/contact-support"
        return support_url

    @property
    def documentation_url(self):
        """
        The documentation url for this item. If no documentation url has been defined,
        a url to the toolkit user guide is returned.
        """
        meta = self._get_manifest()
        doc_url = meta.get("documentation_url")
        if doc_url is None:
            doc_url = "https://help.autodesk.com/view/SGSUB/ENU/?guid=SG_Supervisor_Artist_sa_integrations_sa_integrations_user_guide_html"
        return doc_url

    @property
    def deprecation_status(self):
        """
        Information about deprecation status.

        :returns: Returns a tuple (is_deprecated, message) to indicate
                  if this item is deprecated.
        """
        return self._io_descriptor.get_deprecation_status()

    @property
    def system_name(self):
        """
        A short name, suitable for use in configuration files and for folders on disk.
        """
        return self._io_descriptor.get_system_name()

    @property
    def version(self):
        """
        The version number string for this item.
        """
        return self._io_descriptor.get_version()

    def get_path(self):
        """
        Returns the path to a location where this item is cached.

        When locating the item, any bundle cache fallback paths
        will first be searched in the order they have been defined,
        and lastly the main bundle cached will be checked.

        If the item is not locally cached, ``None`` is returned.

        :returns: Path string or ``None`` if not cached.
        """
        return self._io_descriptor.get_path()

    @property
    def changelog(self):
        """
        Information about the changelog for this item.

        :returns: A tuple (changelog_summary, changelog_url). Values may be ``None``
                  to indicate that no changelog exists.
        """
        return self._io_descriptor.get_changelog()

    def ensure_local(self):
        """
        Helper method. Ensures that the item is locally available.
        """
        return self._io_descriptor.ensure_local()

    def exists_local(self):
        """
        Returns true if this item exists in a local repo.
        """
        return self._io_descriptor.exists_local()

    def download_local(self):
        """
        Retrieves this version to local repo.
        """
        return self._io_descriptor.download_local()

    def find_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.

        .. note:: Different descriptor types implements this logic differently,
                  but general good practice is to follow the semantic version numbering
                  standard for any versions used in conjunction with toolkit. This ensures
                  that toolkit can track and correctly determine not just the latest version
                  but also apply constraint pattern matching such as looking for the latest
                  version matching the pattern ``v1.x.x``. You can read more about semantic
                  versioning here: http://semver.org/

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: instance derived from :class:`Descriptor`
        """
        # make a copy of the descriptor
        latest = copy.copy(self)
        # find latest I/O descriptor
        latest._io_descriptor = self._io_descriptor.get_latest_version(
            constraint_pattern
        )
        return latest

    def find_latest_cached_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version
        that can be found in the local bundle caches.

        .. note:: Different descriptor types implements this logic differently,
                  but general good practice is to follow the semantic version numbering
                  standard for any versions used in conjunction with toolkit. This ensures
                  that toolkit can track and correctly determine not just the latest version
                  but also apply constraint pattern matching such as looking for the latest
                  version matching the pattern ``v1.x.x``. You can read more about semantic
                  versioning here: http://semver.org/

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: Instance derived from :class:`Descriptor` or ``None`` if no cached version
                  is available.
        """
        io_desc = self._io_descriptor.get_latest_cached_version(constraint_pattern)
        if io_desc is None:
            return None

        # make a copy of the descriptor
        latest = copy.copy(self)
        # find latest I/O descriptor
        latest._io_descriptor = io_desc
        return latest

    def has_remote_access(self):
        """
        Probes if the current descriptor is able to handle
        remote requests. If this method returns, true, operations
        such as :meth:`download_local` and :meth:`find_latest_version`
        can be expected to succeed.

        :return: True if a remote is accessible, false if not.
        """
        return self._io_descriptor.has_remote_access()

    # compatibility accessors to ensure that all systems
    # calling this (previously internal!) parts of toolkit
    # will still work.
    def get_display_name(self):
        return self.display_name

    def get_description(self):
        return self.description

    def get_icon_256(self):
        return self.icon_256

    def get_support_url(self):
        return self.support_url

    def get_doc_url(self):
        return self.documentation_url

    def get_deprecation_status(self):
        return self.deprecation_status

    def get_system_name(self):
        return self.system_name

    def get_version(self):
        return self.version

    def get_changelog(self):
        return self.changelog
