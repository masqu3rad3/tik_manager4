# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass

QTPATHS_CMD = "qtpaths6"
MOD_CMD = "pyside6-metaobjectdump"

PYPROJECT_TOML_PATTERN = "pyproject.toml"
PYPROJECT_JSON_PATTERN = "*.pyproject"
# Note that the order is important, as the first pattern that matches is used
PYPROJECT_FILE_PATTERNS = [PYPROJECT_TOML_PATTERN, PYPROJECT_JSON_PATTERN]
QMLDIR_FILE = "qmldir"

QML_IMPORT_NAME = "QML_IMPORT_NAME"
QML_IMPORT_MAJOR_VERSION = "QML_IMPORT_MAJOR_VERSION"
QML_IMPORT_MINOR_VERSION = "QML_IMPORT_MINOR_VERSION"
QT_MODULES = "QT_MODULES"

METATYPES_JSON_SUFFIX = "metatypes.json"
TRANSLATION_SUFFIX = ".ts"
SHADER_SUFFIXES = ".vert", ".frag"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass(frozen=True)
class ClOptions(metaclass=Singleton):
    """
    Dataclass to store the cl options that needs to be passed as arguments.
    """
    dry_run: bool
    quiet: bool
    force: bool
    qml_module: bool


from .utils import (run_command, requires_rebuild, remove_path, package_dir, qtpaths,
                    qt_metatype_json_dir, resolve_valid_project_file)
from .project_data import (is_python_file, ProjectData, QmlProjectData,
                           check_qml_decorators)
from .newproject import new_project, NewProjectTypes
from .design_studio_project import DesignStudioProject
from .pyproject_toml import parse_pyproject_toml, write_pyproject_toml, migrate_pyproject
from .pyproject_json import parse_pyproject_json
