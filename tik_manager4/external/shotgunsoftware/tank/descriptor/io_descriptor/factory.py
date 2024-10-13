# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import copy

from ..errors import TankDescriptorError
from .base import IODescriptorBase

from ... import LogManager

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

log = LogManager.get_logger(__name__)


def create_io_descriptor(
    sg,
    descriptor_type,
    dict_or_uri,
    bundle_cache_root,
    fallback_roots,
    resolve_latest,
    constraint_pattern=None,
    local_fallback_when_disconnected=True,
):
    """
    Factory method. Use this method to construct all DescriptorIO instances.

    A descriptor is immutable in the sense that it always points at the same code -
    this may be a particular frozen version out of that toolkit app store that
    will not change or it may be a dev area where the code can change. Given this,
    descriptors are cached and only constructed once for a given descriptor URL.

    :param sg: Shotgun connection to associated site
    :param descriptor_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK
    :param dict_or_uri: A std descriptor dictionary dictionary or string
    :param bundle_cache_root: Root path to where downloaded apps are cached
    :param fallback_roots: List of immutable fallback cache locations where
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
                                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                                - v0.12.x - get the highest v0.12 version
                                - v1.x.x - get the highest v1 version
    :param local_fallback_when_disconnected: If resolve_latest is set to True, specify the behaviour
                            in the case when no connection to a remote descriptor can be established,
                            for example because and internet connection isn't available. If True, the
                            descriptor factory will attempt to fall back on any existing locally cached
                            bundles and return the latest one available. If False, a
                            :class:`TankDescriptorError` is raised instead.

    :returns: Descriptor object
    :raises: :class:`TankDescriptorError`
    """
    # resolve into both dict and uri form
    if isinstance(dict_or_uri, str):
        descriptor_dict = IODescriptorBase.dict_from_uri(dict_or_uri)
    else:
        # make a copy to make sure the original object is never altered
        descriptor_dict = copy.deepcopy(dict_or_uri)

    # at this point we didn't have a cache hit,
    # so construct the object manually
    if resolve_latest and is_descriptor_version_missing(descriptor_dict):
        # if someone is requesting a latest descriptor and not providing a version token
        # make sure to add an artificial one so that we can resolve it.
        descriptor_dict["version"] = "latest"

    # Ensure that the descrptor version is a str.  For some descriptors a
    # verson is not expected, so if the key doesn't exist we'll do nothing.
    if isinstance(descriptor_dict.get("version"), str):
        # On Python 2 this will have no effect, but on Python 3, we will decode
        # bytes to a str.
        descriptor_dict["version"] = sgutils.ensure_str(descriptor_dict["version"])

    # instantiate the Descriptor
    descriptor = IODescriptorBase.create(descriptor_type, descriptor_dict, sg)

    # specify where to go look for caches
    descriptor.set_cache_roots(bundle_cache_root, fallback_roots)

    if resolve_latest:
        # attempt to get "remote" latest first
        # and if that fails, fall back on the latest item
        # available in the local cache.
        log.debug("Trying to resolve latest version...")
        if descriptor.has_remote_access():
            log.debug(
                "Remote connection is available - attempting to get latest version from remote..."
            )
            descriptor = descriptor.get_latest_version(constraint_pattern)
            log.debug("Resolved latest to be %r" % descriptor)

        else:
            if local_fallback_when_disconnected:
                # get latest from bundle cache
                log.warning(
                    "Remote connection is not available - will try to get "
                    "the latest locally cached version of %s..." % descriptor
                )
                latest_cached_descriptor = descriptor.get_latest_cached_version(
                    constraint_pattern
                )
                if latest_cached_descriptor is None:
                    log.warning(
                        "No locally cached versions of %r available." % descriptor
                    )
                    raise TankDescriptorError(
                        "Could not get latest version of %s. "
                        "For more details, see the log." % descriptor
                    )
                log.debug(
                    "Latest locally cached descriptor is %r" % latest_cached_descriptor
                )
                descriptor = latest_cached_descriptor

            else:
                # do not attempt to get the latest locally cached version
                log.warning(
                    "Remote connection not available to determine latest version."
                )
                raise TankDescriptorError(
                    "Could not get latest version of %s. "
                    "For more details, see the log." % descriptor
                )

    return descriptor


def is_descriptor_version_missing(dict_or_uri):
    """
    Helper method which checks if a descriptor needs a version.

    If the given descriptor dictionary or uri is one of the
    types which requires a version token, and this token is not
    defined, ``True`` will be returned, otherwise ``False``.

    This is useful for a standard pattern which can be used used
    where you want to allow users to configure toolkit
    descriptors which track either the latest version or a specific one.
    In this pattern, the user hints that they want to track latest
    version by omitting the version token altogether.

    The following standard pattern can then be implemented::

        # determine if we should request the latest version
        # of the given descriptor
        if is_descriptor_version_missing(descriptor_uri):
            # require the descriptor system to return
            # the latest descriptor it can detect
            resolve_latest = True
        else:
            # normal direct lookup of a particular
            # descriptor version
            resolve_latest = False

        descriptor_obj = create_descriptor(
            sg_connection,
            Descriptor.CONFIG,
            descriptor_uri,
            resolve_latest=resolve_latest
        )

    :param dict_or_uri: A std descriptor dictionary dictionary or string
    :return: Boolean to indicate if a required version token is missing
    """
    # resolve into both dict and uri form
    if isinstance(dict_or_uri, str):
        descriptor_dict = descriptor_uri_to_dict(dict_or_uri)
    else:
        # make a copy to make sure the original object is never altered
        descriptor_dict = dict_or_uri

    # We only do this for descriptor types that supports a version number concept
    descriptors_using_version = ["app_store", "shotgun", "manual", "git", "git_branch"]

    if (
        "version" not in descriptor_dict
        and descriptor_dict.get("type") in descriptors_using_version
    ):
        return True
    else:
        return False


def descriptor_uri_to_dict(uri):
    """
    Translates a descriptor uri into a dictionary.

    :param uri: descriptor string uri
    :returns: descriptor dictionary
    """
    return IODescriptorBase.dict_from_uri(uri)


def descriptor_dict_to_uri(ddict):
    """
    Translates a descriptor dictionary into a uri.

    :param ddict: descriptor dictionary
    :returns: descriptor uri
    """
    return IODescriptorBase.uri_from_dict(ddict)
