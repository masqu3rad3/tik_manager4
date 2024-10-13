# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


# Shotgun: The entity that represents Pipeline Configurations in Shotgun
PIPELINE_CONFIGURATION_ENTITY_TYPE = "PipelineConfiguration"

# the manifest file inside a bundle
BUNDLE_METADATA_FILE = "info.yml"

# the generation of the logic that handles cloud based deploy.
# if major changes happen to the way cloud based configs are handled
# by the system, for example requiring any existing deployed cloud
# configs to be re-deployed, this version number should be incremented.
BOOTSTRAP_LOGIC_GENERATION = 8

# config file with information about which core to use
CONFIG_CORE_DESCRIPTOR_FILE = "core_api.yml"

# the file that defines which storages a configuration requires
STORAGE_ROOTS_FILE = "roots.yml"

# the implied main storage
PRIMARY_STORAGE_NAME = "primary"

# Configuration file containing shotgun site details
CONFIG_SHOTGUN_FILE = "shotgun.yml"

# Configuration file containing setup and path details
PIPELINECONFIG_FILE = "pipeline_configuration.yml"

# The name of the primary pipeline config
PRIMARY_PIPELINE_CONFIG_NAME = "Primary"

# The name of an unmanaged pipeline config
# Unmanaged pipeline configs don't have a corresponding
# record in Shotgun.
UNMANAGED_PIPELINE_CONFIG_NAME = "Unmanaged"

# The project name for a project with no tank name
# not having a Project.tank_name is okay as long as
# the configuration doesn't use templates.
UNNAMED_PROJECT_NAME = "unnamed"

# latest core
LATEST_CORE_DESCRIPTOR = {"type": "app_store", "name": "tk-core"}

# default PTR desktop app python installations
DESKTOP_PYTHON_MAC = "/Applications/Shotgun.app/Contents/Resources/Python/bin/python"
DESKTOP_PYTHON_WIN = "C:\\Program Files\\Shotgun\\Python\\python.exe"
DESKTOP_PYTHON_LINUX = "/opt/Shotgun/Python/bin/python"

# name of the special baked descriptor that is used to
# avoid locally cache immutable bootstrap setups
BAKED_DESCRIPTOR_TYPE = "baked"
BAKED_DESCRIPTOR_FOLDER_NAME = "baked"

# environment variable that can be used to override the
# configuration loaded when a bootstrap/plugin is starting up.
CONFIG_OVERRIDE_ENV_VAR = "TK_BOOTSTRAP_CONFIG_OVERRIDE"

# environment variable that is used to indicate a specific
# pipeline configuration to be used.
PIPELINE_CONFIG_ID_ENV_VAR = "SHOTGUN_PIPELINE_CONFIGURATION_ID"

# environment variable that is used to indicate which bundle caches to be used.
BUNDLE_CACHE_FALLBACK_PATHS_ENV_VAR = "SHOTGUN_BUNDLE_CACHE_FALLBACK_PATHS"

# the name of the folder within the config where bundles are cached.
BUNDLE_CACHE_FOLDER_NAME = "bundle_cache"

# the shotgun engine always has this name
SHOTGUN_ENGINE_NAME = "tk-shotgun"

# This is the maximum version of tk-config-basic
# supporting Python 2.
MAX_CONFIG_BASIC_PYTHON2_SUPPORTED = "v1.4.6"
