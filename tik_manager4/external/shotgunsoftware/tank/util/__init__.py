# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .platforms import is_windows, is_linux, is_macos
from .shotgun import register_publish
from .shotgun import resolve_publish_path
from .shotgun import find_publish
from .shotgun import download_url
from .shotgun import create_event_log_entry
from .shotgun import get_entity_type_display_name
from .shotgun import get_published_file_entity_type

from .version import (
    is_version_older,
    is_version_newer,
    is_version_older_or_equal,
    is_version_newer_or_equal,
    suppress_known_deprecation,
)

from .shotgun_entity import get_sg_entity_name_field

from .environment import append_path_to_env_var
from .environment import prepend_path_to_env_var

from .login import get_shotgun_user
from .login import get_current_user

# DO keep the following two log_user_*_metric to preserve retro
# compatibility and prevent exception in legacy engine code.
from .metrics import log_user_activity_metric
from .metrics import log_user_attribute_metric
from .metrics import EventMetric
from .shotgun_path import ShotgunPath

from . import filesystem
from . import json
from . import pickle

from .local_file_storage import LocalFileStorageManager

from .errors import PublishResolveError
from .errors import UnresolvableCoreConfigurationError, ShotgunAttachmentDownloadError
from .errors import EnvironmentVariableFileLookupError, ShotgunPublishError
from .errors import PublishResolveError
from .errors import PublishPathNotDefinedError, PublishPathNotSupported

from .user_settings import UserSettings

from .storage_roots import StorageRoots
