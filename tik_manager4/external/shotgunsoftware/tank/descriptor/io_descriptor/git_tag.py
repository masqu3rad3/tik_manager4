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
import re

from .git import IODescriptorGit
from ..errors import TankDescriptorError
from ... import LogManager

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

log = LogManager.get_logger(__name__)


class IODescriptorGitTag(IODescriptorGit):
    """
    Represents a tag in a git repository.

    location: {"type": "git", "path": "/path/to/repo.git", "version": "v0.2.1"}

    The payload cached in the bundle cache is not a git repo
    but only contains the tag given by the version pass with
    the descriptor.

    path can be on the form:

        git@github.com:manneohrstrom/tk-hiero-publish.git
        https://github.com/manneohrstrom/tk-hiero-publish.git
        git://github.com/manneohrstrom/tk-hiero-publish.git
        /full/path/to/local/repo.git
    """

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: descriptor dictionary describing the bundle
        :param sg_connection: Shotgun connection to associated site.
        :param bundle_type: The type of bundle. ex: Descriptor.APP
        :return: Descriptor instance
        """
        # make sure all required fields are there
        self._validate_descriptor(
            descriptor_dict, required=["type", "path", "version"], optional=[]
        )

        # call base class
        super(IODescriptorGitTag, self).__init__(
            descriptor_dict, sg_connection, bundle_type
        )

        # path is handled by base class - all git descriptors
        # have a path to a repo
        self._version = descriptor_dict.get("version")
        self._sg_connection = sg_connection
        self._bundle_type = bundle_type

    def __str__(self):
        """
        Human readable representation
        """
        # git@github.com:manneohrstrom/tk-hiero-publish.git, tag v1.2.3
        return "%s, Tag %s" % (self._path, self._version)

    def _get_bundle_cache_path(self, bundle_cache_root):
        """
        Given a cache root, compute a cache path suitable
        for this descriptor, using the 0.18+ path format.

        :param bundle_cache_root: Bundle cache root path
        :return: Path to bundle cache location
        """
        # git@github.com:manneohrstrom/tk-hiero-publish.git -> tk-hiero-publish.git
        # /full/path/to/local/repo.git -> repo.git
        name = os.path.basename(self._path)

        return os.path.join(bundle_cache_root, "git", name, self.get_version())

    def _get_cache_paths(self):
        """
        Get a list of resolved paths, starting with the primary and
        continuing with alternative locations where it may reside.

        Note: This method only computes paths and does not perform any I/O ops.

        :return: List of path strings
        """
        # get default cache paths from base class
        paths = super(IODescriptorGitTag, self)._get_cache_paths()

        # for compatibility with older versions of core, prior to v0.18.x,
        # add the old-style bundle cache path as a fallback. As of v0.18.x,
        # the bundle cache subdirectory names were shortened and otherwise
        # modified to help prevent MAX_PATH issues on windows. This call adds
        # the old path as a fallback for cases where core has been upgraded
        # for an existing project. NOTE: This only works because the bundle
        # cache root didn't change (when use_bundle_cache is set to False).
        # If the bundle cache root changes across core versions, then this will
        # need to be refactored.

        # git@github.com:manneohrstrom/tk-hiero-publish.git -> tk-hiero-publish.git
        # /full/path/to/local/repo.git -> repo.git
        name = os.path.basename(self._path)

        legacy_folder = self._get_legacy_bundle_install_folder(
            "git", self._bundle_cache_root, self._bundle_type, name, self.get_version()
        )
        if legacy_folder:
            paths.append(legacy_folder)

        return paths

    def get_version(self):
        """
        Returns the version number string for this item, .e.g 'v1.2.3'
        """
        return self._version

    def _download_local(self, destination_path):
        """
        Retrieves this version to local repo.
        Will exit early if app already exists local.

        This will connect to remote git repositories.
        Depending on how git is configured, https repositories
        requiring credentials may result in a shell opening up
        requesting username and password.

        The git repo will be cloned into the local cache and
        will then be adjusted to point at the relevant tag.

        :param destination_path: The destination path on disk to which
        the git tag descriptor is to be downloaded to.
        """
        try:
            # clone the repo, checkout the given tag
            self._clone_then_execute_git_commands(
                destination_path, [], depth=1, ref=self._version
            )
        except Exception as e:
            raise TankDescriptorError(
                "Could not download %s, " "tag %s: %s" % (self._path, self._version, e)
            )

    def get_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.

        This will connect to remote git repositories.
        Depending on how git is configured, https repositories
        requiring credentials may result in a shell opening up
        requesting username and password.

        This will clone the git repository into a temporary location in order to
        introspect its properties.

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: IODescriptorGitTag object
        """
        if constraint_pattern:
            tag_name = self._get_latest_by_pattern(constraint_pattern)
        else:
            tag_name = self._get_latest_version()

        new_loc_dict = copy.deepcopy(self._descriptor_dict)
        new_loc_dict["version"] = sgutils.ensure_str(tag_name)

        # create new descriptor to represent this tag
        desc = IODescriptorGitTag(new_loc_dict, self._sg_connection, self._bundle_type)
        desc.set_cache_roots(self._bundle_cache_root, self._fallback_roots)
        return desc

    def _get_latest_by_pattern(self, pattern):
        """
        Returns a descriptor object that represents the latest
        version, but based on a version pattern.

        :param pattern: Version patterns are on the following forms:
            - v1.2.3 (can return this v1.2.3 but also any forked version under, eg. v1.2.3.2)
            - v1.2.x (examples: v1.2.4, or a forked version v1.2.4.2)
            - v1.x.x (examples: v1.3.2, a forked version v1.3.2.2)
            - v1.2.3.x (will always return a forked version, eg. v1.2.3.2)
        :returns: IODescriptorGitTag object
        """
        git_tags = self._fetch_tags()
        latest_tag = self._find_latest_tag_by_pattern(git_tags, pattern)
        if latest_tag is None:
            raise TankDescriptorError(
                "'%s' does not have a version matching the pattern '%s'. "
                "Available versions are: %s"
                % (self.get_system_name(), pattern, ", ".join(git_tags))
            )

        return latest_tag

    def _fetch_tags(self):
        try:
            # clone the repo, list all tags
            # for the repository, across all branches
            commands = ["ls-remote -q --tags %s" % self._path]
            tags = self._tmp_clone_then_execute_git_commands(commands, depth=1).split(
                "\n"
            )
            regex = re.compile(".*refs/tags/([^^]*)$")
            git_tags = []
            for tag in tags:
                m = regex.match(sgutils.ensure_str(tag))
                if m:
                    git_tags.append(m.group(1))

        except Exception as e:
            raise TankDescriptorError(
                "Could not get list of tags for %s: %s" % (self._path, e)
            )

        if len(git_tags) == 0:
            raise TankDescriptorError(
                "Git repository %s doesn't have any tags!" % self._path
            )

        return git_tags

    def _get_latest_version(self):
        """
        Returns a descriptor object that represents the latest version.
        :returns: IODescriptorGitTag object
        """
        tags = self._fetch_tags()
        latest_tag = self._find_latest_tag_by_pattern(tags, pattern=None)
        if latest_tag is None:
            raise TankDescriptorError(
                "Git repository %s doesn't have any tags!" % self._path
            )

        return latest_tag

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
        all_versions = list(self._get_locally_cached_versions().keys())
        log.debug("Found %d versions" % len(all_versions))

        if len(all_versions) == 0:
            return None

        # get latest
        version_to_use = self._find_latest_tag_by_pattern(
            all_versions, constraint_pattern
        )
        if version_to_use is None:
            return None

        # create new descriptor to represent this tag
        new_loc_dict = copy.deepcopy(self._descriptor_dict)
        new_loc_dict["version"] = version_to_use
        desc = IODescriptorGitTag(new_loc_dict, self._sg_connection, self._bundle_type)
        desc.set_cache_roots(self._bundle_cache_root, self._fallback_roots)

        log.debug("Latest cached version resolved to %r" % desc)
        return desc
