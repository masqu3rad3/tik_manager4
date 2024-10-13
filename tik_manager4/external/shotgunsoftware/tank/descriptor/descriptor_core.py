# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .descriptor import Descriptor
from .errors import TankMissingManifestError
from . import constants


class CoreDescriptor(Descriptor):
    """
    Descriptor object which describes a Toolkit Core API version.
    """

    def __init__(
        self, sg_connection, io_descriptor, bundle_cache_root_override, fallback_roots
    ):
        """
        .. note:: Use the factory method :meth:`create_descriptor` when
                  creating new descriptor objects.

        :param sg_connection: Connection to the current site.
        :param io_descriptor: Associated IO descriptor.
        :param bundle_cache_root_override: Override for root path to where
            downloaded apps are cached.
        :param fallback_roots: List of immutable fallback cache locations where
            apps will be searched for.
        """
        super(CoreDescriptor, self).__init__(io_descriptor)

    @property
    def version_constraints(self):
        """
        A dictionary with version constraints. The absence of a key
        indicates that there is no defined constraint. The following keys can be
        returned: min_sg, min_core, min_engine and min_desktop

        :returns: Dictionary with optional keys min_sg, min_core,
                  min_engine, min_desktop
        """
        constraints = {}

        manifest = self._get_manifest()

        constraints["min_sg"] = manifest.get(
            "requires_shotgun_version", constants.LOWEST_SHOTGUN_VERSION
        )

        return constraints

    def get_feature_info(self, feature_name, default_value=None):
        """
        Retrieves information for a given feature in the manifest.

        The ``default_value`` will be returned in the following cases:
            - a feature is missing from the manifest
            - the manifest is empty
            - the manifest is missing

        :param str feature_name: Name of the feature to retrieve from the manifest.
        :param object default_value: Value to return if the feature is missing.

        :returns: The value for the feature if present, ``default_value`` otherwise.
        """
        infos = self.get_features_info()
        if feature_name in infos:
            return infos[feature_name]
        else:
            return default_value

    def get_features_info(self):
        """
        Retrieves the feature dictionary from the manifest.

        If the manifest if empty or missing, an empty dictionary will be returned.

        :returns: Dictionary of features.
        """
        try:
            manifest = self._get_manifest() or {}
        except TankMissingManifestError:
            return {}
        return manifest.get("features") or {}

    def copy(self, target_folder):
        """
        Copy the config descriptor into the specified target location.

        :param target_folder: Folder to copy the descriptor to
        """
        self._io_descriptor.copy(target_folder, skip_list=["tests", "docs"])
