# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# pending QA environment variable
APP_STORE_QA_MODE_ENV_VAR = "TANK_QA_ENABLED"

# app store: the entity that represents the core api
TANK_CORE_VERSION_ENTITY_TYPE = "CustomNonProjectEntity01"

# app store: the entity representing apps
TANK_APP_ENTITY_TYPE = "CustomNonProjectEntity02"

# app store: the entity representing app versions
TANK_APP_VERSION_ENTITY_TYPE = "CustomNonProjectEntity05"

# app store: the entity representing engines
TANK_ENGINE_ENTITY_TYPE = "CustomNonProjectEntity03"

# app store: the entity representing engine versions
TANK_ENGINE_VERSION_ENTITY_TYPE = "CustomNonProjectEntity04"

# app store: the entity representing frameworks
TANK_FRAMEWORK_ENTITY_TYPE = "CustomNonProjectEntity13"

# app store: the entity representing framework versions
TANK_FRAMEWORK_VERSION_ENTITY_TYPE = "CustomNonProjectEntity09"

# app store: the entity representing configs
TANK_CONFIG_ENTITY_TYPE = "CustomNonProjectEntity07"

# app store: the entity representing config versions
TANK_CONFIG_VERSION_ENTITY_TYPE = "CustomNonProjectEntity08"

# app store: the field containing the zip payload
TANK_CODE_PAYLOAD_FIELD = "sg_payload"

# app store: dummy project required when writing event data to the system
TANK_APP_STORE_DUMMY_PROJECT = {"type": "Project", "id": 64}

# the location of the toolkit app store
SGTK_APP_STORE = "https://tank.shotgunstudio.com"

# timeout in secs to apply to TK app store connections
SGTK_APP_STORE_CONN_TIMEOUT = 5

# the manifest file inside a bundle
BUNDLE_METADATA_FILE = "info.yml"

# readme file for toolkit configurations
CONFIG_README_FILE = "README"

# config file with information about which core to use
CONFIG_CORE_DESCRIPTOR_FILE = "core_api.yml"

# the file that defines which storages a configuration requires
STORAGE_ROOTS_FILE = "roots.yml"

# the implied main storage
PRIMARY_STORAGE_NAME = "primary"

# descriptor uri separator
DESCRIPTOR_URI_PATH_SCHEME = "sgtk"
DESCRIPTOR_URI_PATH_PREFIX = "descriptor"
DESCRIPTOR_URI_SEPARATOR = ":"

# This is the earliest version of Shotgun that Toolkit has historically been compatible
# with. Code that use this constant do so because the manifest from a core doesn't
# have a requires_shotgun_version. 5.0.0 is the minimum Shotgun version that every
# version fo Toolkit have been published with ever since it came out.
LOWEST_SHOTGUN_VERSION = "5.0.0"

# name of the app store specific proxy setting
APP_STORE_HTTP_PROXY = "app_store_http_proxy"

# environment variable used to indicate the primary bundle cache path to be used.
BUNDLE_CACHE_PATH_ENV_VAR = "SHOTGUN_BUNDLE_CACHE_PATH"

# environment variable used to disable connection to the app store
DISABLE_APPSTORE_ACCESS_ENV_VAR = "SHOTGUN_DISABLE_APPSTORE_ACCESS"

# the Descriptor types
(
    DESCRIPTOR_APP,
    DESCRIPTOR_FRAMEWORK,
    DESCRIPTOR_ENGINE,
    DESCRIPTOR_CONFIG,
    DESCRIPTOR_CORE,
    DESCRIPTOR_INSTALLED_CONFIG,
) = range(6)
