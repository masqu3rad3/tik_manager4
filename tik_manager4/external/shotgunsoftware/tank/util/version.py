# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
import warnings
import contextlib
import sys

if sys.version_info[0:2] < (3, 10):
    from distutils.version import LooseVersion
else:
    try:
        from setuptools._distutils.version import LooseVersion
    except ModuleNotFoundError:
        # Known issue with VRED 16. Unable to load the setuptools module
        from distutils.version import LooseVersion

from . import sgre as re
from ..errors import TankError


GITHUB_HASH_RE = re.compile("^[0-9a-fA-F]{7,40}$")


def is_version_head(version):
    """
    Returns if the specified version is HEAD or MASTER. The comparison is case insensitive.

    :param version: Version to test.

    :returns: True if version is HEAD or MASTER, false otherwise.
    """
    return version.lower() in ["head", "master"]


def _is_git_commit(version):
    """
    Returns if the version looks like a git commit id.

    :param version: Version to test.

    :returns: True if the version is a commit id, false otherwise.
    """
    return GITHUB_HASH_RE.match(version) is not None


def is_version_newer(a, b):
    """
    Is the version string ``a`` newer than ``b``?

    If one of the version is `master`, `head`, or formatted like a git commit sha,
    it is considered more recent than the other version.

    :raises TankError: Raised if the two versions are different git commit shas, as
        they can't be compared.

    :returns: ``True`` if ``a`` is newer than ``b`` but not equal, ``False`` otherwise.
    """
    return _compare_versions(a, b)


def is_version_older(a, b):
    """
    Is the version string ``a`` older than ``b``?

    If one of the version is `master`, `head`, or formatted like a git commit sha,
    it is considered more recent than the other version.

    :raises TankError: Raised if the two versions are different git commit shas, as
        they can't be compared.

    :returns: ``True`` if ``a`` is older than ``b`` but not equal, ``False`` otherwise.
    """
    return _compare_versions(b, a)


def is_version_newer_or_equal(a, b):
    """
    Is the version string ``a`` newer than or equal to ``b``?

    If one of the version is `master`, `head`, or formatted like a git commit sha,
    it is considered more recent than the other version.

    :raises TankError: Raised if the two versions are different git commit shas, as
        they can't be compared.

    :returns: ``True`` if ``a`` is newer than or equal to ``b``, ``False`` otherwise.
    """
    return is_version_older(a, b) is False


def is_version_older_or_equal(a, b):
    """
    Is the version string ``a`` older than or equal to ``b``?

    If one of the version is `master`, `head`, or formatted like a git commit sha,
    it is considered more recent than the other version.

    :raises TankError: Raised if the two versions are different git commit shas, as
        they can't be compared.

    :returns: ``True`` if ``a`` is older than or equal to ``b``, ``False`` otherwise.
    """
    return is_version_newer(a, b) is False


def is_version_number(version):
    r"""
    Tests whether the given string is a properly formed
    version number (ex: v1.2.3). The test is made using
    the pattern r"v\d+.\d+.\d+$"

    :param str version: The version string to test.

    :rtype: bool
    """
    match = re.match(r"v\d+.\d+.\d+$", version)

    if match:
        return True
    else:
        return False


@contextlib.contextmanager
def suppress_known_deprecation():
    """
    Imported function from setuptools.distutils module
    """
    with warnings.catch_warnings(record=True) as ctx:
        warnings.filterwarnings(
            action="default",
            category=DeprecationWarning,
            message="distutils Version classes are deprecated.",
        )
        yield ctx


def _compare_versions(a, b):
    """
    Tests if version a is newer than version b.

    :param str a: The first version string to compare.
    :param str b: The second version string to compare.

    :rtype: bool
    """
    if b in [None, "Undefined"]:
        # a is always newer than None or `Undefined`
        return True

    if _is_git_commit(a) and not _is_git_commit(b):
        return True
    elif _is_git_commit(b) and not _is_git_commit(a):
        return False
    elif _is_git_commit(a) and _is_git_commit(b):
        if a.lower() == b.lower():
            return False
        else:
            raise TankError("Can't compare two git commits lexicographically.")

    if is_version_head(a):
        # our version is latest
        return True

    if is_version_head(b):
        # comparing against HEAD - our version is always old
        return False

    if a.startswith("v"):
        a = a[1:]
    if b.startswith("v"):
        b = b[1:]

    # In Python 3, LooseVersion comparisons between versions where a non-numeric
    # version component is compared to a numeric one fail.  We'll work around this
    # as follows:
    # First, try to use LooseVersion for comparison.  This should work in
    # most cases.
    try:
        with suppress_known_deprecation():
            # Supress `distutils Version classes are deprecated.` for Python 3.10
            version_a = LooseVersion(a).version
            version_b = LooseVersion(b).version

            version_num_a = []
            version_num_b = []
            # taking only the integers of the version to make comparison
            for version in version_a:
                if isinstance(version, (int)):
                    version_num_a.append(version)
                elif version == "-":
                    break
            for version in version_b:
                if isinstance(version, (int)):
                    version_num_b.append(version)
                elif version == "-":
                    break

            # Comparing equal number versions with with one of them with '-' appended, if a version
            # has '-' appended it's older than the same version with '-' at the end
            if version_num_a == version_num_b:
                if "-" in a and "-" not in b:
                    return False  # False, version a is older than b
                elif "-" in b and "-" not in a:
                    return True  # True, version a is older than b
                else:
                    return LooseVersion(a) > LooseVersion(
                        b
                    )  # If both has '-' compare '-rcx' versions
            else:
                return LooseVersion(a) > LooseVersion(
                    b
                )  # If they are different numeric versions
    except TypeError:
        # To mimick the behavior in Python 2.7 as closely as possible, we will
        # If LooseVersion comparison didn't work, try to extract a numeric
        # version from both versions for comparison
        version_expr = re.compile(r"^((?:\d+)(?:\.\d+)*)(.+)$")
        match_a = version_expr.match(a)
        match_b = version_expr.match(b)
        if match_a and match_b:
            # If we could get two numeric versions, generate LooseVersions for
            # them.
            ver_a = LooseVersion(match_a.group(1))
            ver_b = LooseVersion(match_b.group(1))
            if ver_a != ver_b:
                # If they're not identical, return based on this comparison
                return ver_a > ver_b
            else:
                # If the numeric versions do match, do a string comparsion for
                # the rest.
                return match_a.group(2) > match_b.group(2)
        elif match_a or match_b:
            # If only one had a numeric version, treat that as the newer version.
            return bool(match_a)

    # In the case that both versions are non-numeric, do a string comparison.
    return a > b
