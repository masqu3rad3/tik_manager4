# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from .descriptor import Descriptor, create_descriptor
from .descriptor_core import CoreDescriptor
from .descriptor_bundle import AppDescriptor, FrameworkDescriptor, EngineDescriptor
from .descriptor_config import ConfigDescriptor

from .errors import (
    TankAppStoreConnectionError,
    TankAppStoreError,
    TankDescriptorError,
    InvalidAppStoreCredentialsError,
    TankInvalidAppStoreCredentialsError,
    CheckVersionConstraintsError,
    TankCheckVersionConstraintsError,
    TankInvalidInterpreterLocationError,
    TankMissingManifestError,
)

from .io_descriptor import (
    descriptor_dict_to_uri,
    descriptor_uri_to_dict,
    is_descriptor_version_missing,
)


def _initialize_descriptor_factory():
    """
    Register the descriptor subclass with the Descriptor base class factory.
    This complex process for handling the descriptor abstract factory
    management is in order to avoid local imports in classes.
    """
    from .descriptor_cached_config import CachedConfigDescriptor
    from .descriptor_installed_config import InstalledConfigDescriptor

    Descriptor.register_descriptor_factory(Descriptor.APP, AppDescriptor)
    Descriptor.register_descriptor_factory(Descriptor.ENGINE, EngineDescriptor)
    Descriptor.register_descriptor_factory(Descriptor.FRAMEWORK, FrameworkDescriptor)
    Descriptor.register_descriptor_factory(Descriptor.CONFIG, CachedConfigDescriptor)
    Descriptor.register_descriptor_factory(
        Descriptor.INSTALLED_CONFIG, InstalledConfigDescriptor
    )
    Descriptor.register_descriptor_factory(Descriptor.CORE, CoreDescriptor)


_initialize_descriptor_factory()
del _initialize_descriptor_factory
