# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .factory import (
    create_io_descriptor,
    descriptor_uri_to_dict,
    descriptor_dict_to_uri,
    is_descriptor_version_missing,
)


def _initialize_descriptor_factory():
    """
    Register the IODescriptor subclasses with the IODescriptorBase factory.
    This complex process for handling the IODescriptor abstract factory
    management is in order to avoid local imports in classes.
    """
    from .base import IODescriptorBase
    from .appstore import IODescriptorAppStore
    from .dev import IODescriptorDev
    from .path import IODescriptorPath
    from .shotgun_entity import IODescriptorShotgunEntity
    from .git_tag import IODescriptorGitTag
    from .git_branch import IODescriptorGitBranch
    from .github_release import IODescriptorGithubRelease
    from .manual import IODescriptorManual

    IODescriptorBase.register_descriptor_factory("app_store", IODescriptorAppStore)
    IODescriptorBase.register_descriptor_factory("dev", IODescriptorDev)
    IODescriptorBase.register_descriptor_factory("path", IODescriptorPath)
    IODescriptorBase.register_descriptor_factory("shotgun", IODescriptorShotgunEntity)
    IODescriptorBase.register_descriptor_factory("git", IODescriptorGitTag)
    IODescriptorBase.register_descriptor_factory("git_branch", IODescriptorGitBranch)
    IODescriptorBase.register_descriptor_factory(
        "github_release", IODescriptorGithubRelease
    )
    IODescriptorBase.register_descriptor_factory("manual", IODescriptorManual)


_initialize_descriptor_factory()
del _initialize_descriptor_factory
