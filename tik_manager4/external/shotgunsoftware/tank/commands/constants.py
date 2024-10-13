# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# flag to pass for legacy yaml parser
LEGACY_YAML_PARSER_FLAG = "--use-legacy-yaml"

# metadata file for engines and apps
BUNDLE_METADATA_FILE = "info.yml"

# the storage name that is treated to be the primary storage for tank
PRIMARY_STORAGE_NAME = "primary"

# the name of the file that contains the storage root definitions
STORAGE_ROOTS_FILE = "roots.yml"

# app store: the entity representing configs
TANK_CONFIG_ENTITY = "CustomNonProjectEntity07"

# app store: the entity representing config versions
TANK_CONFIG_VERSION_ENTITY = "CustomNonProjectEntity08"

# app store: the field containing the zip payload
TANK_CODE_PAYLOAD_FIELD = "sg_payload"

# Configuration file containing setup and path details
PIPELINECONFIG_FILE = "pipeline_configuration.yml"

# Shotgun: The entity that represents Pipeline Configurations in Shotgun
PIPELINE_CONFIGURATION_ENTITY = "PipelineConfiguration"

# field to which configs should be uploaded in Shotgun
PIPELINE_CONFIGURATION_UPLOAD_FIELD = "uploaded_config"

# the name of the primary pipeline configuration
PRIMARY_PIPELINE_CONFIG_NAME = "Primary"

# the plugin id pattern to use by default in shotgun
DEFAULT_PLUGIN_ID = "basic.*"

# The name of the default config
DEFAULT_CFG = "tk-config-default2"

# the name of the shell engine
SHELL_ENGINE = "tk-shell"
