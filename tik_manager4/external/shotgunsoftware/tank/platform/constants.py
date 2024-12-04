# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Constants relating to the app/engine part of the Tank Stack.

(for constants relating to the low level part of the tank stack, see ..constants)

"""

# metadata file for engines and apps
BUNDLE_METADATA_FILE = "info.yml"

# Valid data types for use in app/engine settings schemas
TANK_SCHEMA_VALID_TYPES = [
    "str",
    "int",
    "float",
    "bool",
    "list",
    "dict",
    "tank_type",
    "publish_type",
    "template",
    "hook",
    "shotgun_entity_type",
    "shotgun_permission_group",
    "shotgun_filter",
    "config_path",
]

# Types from the list above that expect "str" values.
TANK_SCHEMA_STRING_TYPES = [
    "tank_type",
    "publish_type",
    "template",
    "hook",
    "shotgun_entity_type",
    "shotgun_permission_group",
    "config_path",
]

# a folder to look for an automatically add to the pythonpath
BUNDLE_PYTHON_FOLDER = "python"

# force use old, non-structure preseving parser
USE_LEGACY_YAML_ENV_VAR = "TK_USE_LEGACY_YAML"

# the file to look for that defines and bootstraps an engine
ENGINE_FILE = "engine.py"

# the file to look for that defines how to launch a DCC for a given engine
ENGINE_SOFTWARE_LAUNCHER_FILE = "startup.py"

# inside the engine location, the folder in which to look for apps
ENGINE_APPS_LOCATION = "apps"

# app settings location
ENGINE_APP_SETTINGS_LOCATION = "app_settings"

# inside the engine config location, the folder in which to look for environments
ENGINE_ENV_LOCATIONS = "env"

# the key in the configuration for an engine which holds the environment
ENGINE_CONFIG_ENVIRONMENT_KEY = "environment"

# hook that is executed whenever an engine has initialized
TANK_ENGINE_INIT_HOOK_NAME = "engine_init"

# hook that is executed whenever a bundle has initialized
TANK_BUNDLE_INIT_HOOK_NAME = "bundle_init"

# hook that is execute whenever a context change happens
CONTEXT_CHANGE_HOOK = "context_change"

# flag to indicate that an app command is a legacy style
# shotgun multi select action
LEGACY_MULTI_SELECT_ACTION_FLAG = "shotgun_multi_select_action"

# the name of the file that holds the inverse root defs
# note - this is no longer used by the core itself, but it is still
# being used by the perforce integration to handle
# back tracking. The perforce code requests this constant directly
# from its code.
CONFIG_BACK_MAPPING_FILE = "tank_configs.yml"

# default value for hooks
TANK_BUNDLE_DEFAULT_HOOK_SETTING = "default"

# the key name used to identify default values in a manifest file. used as both
# the actual key as well as the prefix for engine-specific default value keys.
# example: "default_value_tk-maya".
TANK_SCHEMA_DEFAULT_VALUE_KEY = "default_value"

# if the engine name is included in a hook definition, include this in the manifest.
TANK_HOOK_ENGINE_REFERENCE_TOKEN = "{engine_name}"

# hook to choose the environment file given a context
PICK_ENVIRONMENT_CORE_HOOK_NAME = "pick_environment"

# the configuration key inside an environment which holds all the app configs
ENVIRONMENT_CFG_APPS_SECTION = "apps"

# the key that holds the app descriptor dict
ENVIRONMENT_LOCATION_KEY = "location"

# the file to look for that defines and bootstraps an app
APP_FILE = "app.py"

# an optional stylesheet that can be defined by bundles
BUNDLE_STYLESHEET_FILE = "style.qss"

# define our standard stylesheet constants
SG_STYLESHEET_CONSTANTS = {
    "SG_HIGHLIGHT_COLOR": "#18A7E3",
    "SG_ALERT_COLOR": "#FC6246",
    "SG_FOREGROUND_COLOR": "#C8C8C8",
    "SG_LINK_COLOR": "#C8C8C8",
}

# the file to look for that defines and bootstraps a framework
FRAMEWORK_FILE = "framework.py"

# the name of the primary pipeline configuration
PRIMARY_PIPELINE_CONFIG_NAME = "Primary"
UNMANAGED_PIPELINE_CONFIG_NAME = "Unmanaged"

# the shotgun engine always has this name
SHOTGUN_ENGINE_NAME = "tk-shotgun"

# Shotgun: The entity that represents Pipeline Configurations in Shotgun
# (defined here for backwards compatibility with the admin-ui framework)
PIPELINE_CONFIGURATION_ENTITY = "PipelineConfiguration"

# the shell engine is assumed to always have this name
SHELL_ENGINE_NAME = "tk-shell"

# the menu favourites key for an engine
MENU_FAVOURITES_KEY = "menu_favourites"

# the name of the include section in env and template files
SINGLE_INCLUDE_SECTION = "include"

# the name of the includes section in env and template files
MULTI_INCLUDE_SECTION = "includes"

# hook that is executed whenever a cache location should be determined
CACHE_LOCATION_HOOK_NAME = "cache_location"
