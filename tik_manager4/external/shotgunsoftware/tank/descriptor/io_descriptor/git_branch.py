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

from .git import IODescriptorGit, TankGitError, _check_output
from ..errors import TankDescriptorError
from ... import LogManager

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

log = LogManager.get_logger(__name__)


class IODescriptorGitBranch(IODescriptorGit):
    """
    Represents a commit in git, belonging to a particular branch.

    Branch format:
    location: {"type": "git_branch",
               "path": "/path/to/repo.git",
               "branch": "master",
               "version": "17fedd8a4e3c7c004316af5001331ad2c9e14bd5"}

    Short hashes can be used:
    location: {"type": "git_branch",
               "path": "/path/to/repo.git",
               "branch": "master",
               "version": "17fedd8"}

    path can be on the form:

        git@github.com:manneohrstrom/tk-hiero-publish.git
        https://github.com/manneohrstrom/tk-hiero-publish.git
        git://github.com/manneohrstrom/tk-hiero-publish.git
        /full/path/to/local/repo.git

    The hash can be short, as long as it is unique, e.g. it follows the same logic
    that git is using for shortening its hashes. A recommendation is to use the first
    seven digits to describe a hash that is unique within a repository.

    The payload cached in the bundle cache represents the entire git repo,
    adjusted to point at the given branch and commit.
    """

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: descriptor dictionary describing the bundle
        :param sg_connection: Shotgun connection to associated site.
        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        :return: Descriptor instance
        """
        # make sure all required fields are there
        self._validate_descriptor(
            descriptor_dict, required=["type", "path", "version", "branch"], optional=[]
        )

        # call base class
        super(IODescriptorGitBranch, self).__init__(
            descriptor_dict, sg_connection, bundle_type
        )

        # path is handled by base class - all git descriptors
        # have a path to a repo
        self._sg_connection = sg_connection
        self._bundle_type = bundle_type
        self._version = descriptor_dict.get("version")
        self._branch = sgutils.ensure_str(descriptor_dict.get("branch"))

    def __str__(self):
        """
        Human readable representation
        """
        # git@github.com:manneohrstrom/tk-hiero-publish.git, branch master, commit 12313123
        return "%s, Branch %s, Commit %s" % (self._path, self._branch, self._version)

    def _get_bundle_cache_path(self, bundle_cache_root):
        """
        Given a cache root, compute a cache path suitable
        for this descriptor, using the 0.18+ path format.

        :param bundle_cache_root: Bundle cache root path
        :return: Path to bundle cache location
        """
        # If the descriptor is an integer change the version to a string type
        if isinstance(self._version, int):
            self._version = str(self._version)
        # to be MAXPATH-friendly, we only use the first seven chars
        short_hash = self._version[:7]

        # git@github.com:manneohrstrom/tk-hiero-publish.git -> tk-hiero-publish.git
        # /full/path/to/local/repo.git -> repo.git
        name = os.path.basename(self._path)

        return os.path.join(bundle_cache_root, "gitbranch", name, short_hash)

    def get_version(self):
        """
        Returns the version number string for this item, .e.g 'v1.2.3'
        or the branch name 'master'
        """
        return self._version

    def _is_latest_commit(self, version, branch):
        """
        Check if the git_branch descriptor is pointing to the
        latest commit version.
        """
        # first probe to check that git exists in our PATH
        log.debug("Checking if the version is pointing to the latest commit...")
        try:
            output = _check_output(["git", "ls-remote", self._path, branch])
        except:
            log.exception("Unexpected error:")
            raise TankGitError(
                "Cannot execute the 'git' command. Please make sure that git is "
                "installed on your system and that the git executable has been added to the PATH."
            )
        latest_commit = output.split("\t")
        short_latest_commit = latest_commit[0][:7]

        if short_latest_commit != version[:7]:
            return False
        log.debug(
            "This version is pointing to the latest commit %s, lets enable shallow clones"
            % short_latest_commit
        )

        return True

    def _download_local(self, destination_path):
        """
        Retrieves this version to local repo.
        Will exit early if app already exists local.

        This will connect to remote git repositories.
        Depending on how git is configured, https repositories
        requiring credentials may result in a shell opening up
        requesting username and password.

        The git repo will be cloned into the local cache and
        will then be adjusted to point at the relevant commit.

        :param destination_path: The destination path on disk to which
        the git branch descriptor is to be downloaded to.
        """
        depth = None
        is_latest_commit = self._is_latest_commit(self._version, self._branch)
        if is_latest_commit:
            depth = 1
        try:
            # clone the repo, switch to the given branch
            # then reset to the given commit
            commands = ['checkout -q "%s"' % self._version]
            self._clone_then_execute_git_commands(
                destination_path,
                commands,
                depth=depth,
                ref=self._branch,
                is_latest_commit=is_latest_commit,
            )
        except Exception as e:
            raise TankDescriptorError(
                "Could not download %s, branch %s, "
                "commit %s: %s" % (self._path, self._branch, self._version, e)
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

        .. note:: The concept of constraint patterns doesn't apply to
                  git commit hashes and any data passed via the
                  constraint_pattern argument will be ignored by this
                  method implementation.

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: IODescriptorGitBranch object
        """
        if constraint_pattern:
            log.warning(
                "%s does not handle constraint patterns. "
                "Latest version will be used." % self
            )

        try:
            # clone the repo, get the latest commit hash
            # for the given branch
            commands = [
                'checkout -q "%s"' % self._branch,
                "log -n 1 \"%s\" --pretty=format:'%%H'" % self._branch,
            ]
            git_hash = self._tmp_clone_then_execute_git_commands(commands)

        except Exception as e:
            raise TankDescriptorError(
                "Could not get latest commit for %s, "
                "branch %s: %s" % (self._path, self._branch, e)
            )

        # make a new descriptor
        new_loc_dict = copy.deepcopy(self._descriptor_dict)
        new_loc_dict["version"] = sgutils.ensure_str(git_hash)
        desc = IODescriptorGitBranch(
            new_loc_dict, self._sg_connection, self._bundle_type
        )
        desc.set_cache_roots(self._bundle_cache_root, self._fallback_roots)
        return desc

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
        # not possible to determine what 'latest' means in this case
        # so check if the current descriptor exists on disk and in this
        # case return it
        if self.get_path():
            return self
        else:
            # no cached version exists
            return None
