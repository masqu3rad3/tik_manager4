# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
import sys
from pathlib import Path
from textwrap import dedent

MAJOR_VERSION = 6

if sys.platform == "win32":
    IMAGE_FORMAT = ".ico"
    EXE_FORMAT = ".exe"
elif sys.platform == "darwin":
    IMAGE_FORMAT = ".icns"
    EXE_FORMAT = ".app"
else:
    IMAGE_FORMAT = ".jpg"
    EXE_FORMAT = ".bin"

DEFAULT_APP_ICON = str((Path(__file__).parent / f"pyside_icon{IMAGE_FORMAT}").resolve())
DEFAULT_IGNORE_DIRS = {"site-packages", "deployment", ".git", ".qtcreator", "build", "dist",
                       "tests", "doc", "docs", "examples", ".vscode", "__pycache__"}

IMPORT_WARNING_PYSIDE = (f"[DEPLOY] Found 'import PySide6' in file {0}"
                         ". Use 'from PySide6 import <module>' or pass the module"
                         " needed using --extra-modules command line argument")
HELP_EXTRA_IGNORE_DIRS = dedent("""
                                Comma-separated directory names inside the project dir. These
                                directories will be skipped when searching for Python files
                                relevant to the project.

                                Example usage: --extra-ignore-dirs=doc,translations
                                """)

HELP_EXTRA_MODULES = dedent("""
                            Comma-separated list of Qt modules to be added to the application,
                            in case they are not found automatically.

                            This occurs when you have 'import PySide6' in your code instead
                            'from PySide6 import <module>'. The module name is specified
                            by either omitting the prefix of Qt or including it.

                            Example usage 1: --extra-modules=Network,Svg
                            Example usage 2: --extra-modules=QtNetwork,QtSvg
                            """)

# plugins to be removed from the --include-qt-plugins option because these plugins
# don't exist in site-package under PySide6/Qt/plugins
PLUGINS_TO_REMOVE = ["accessiblebridge", "platforms/darwin", "networkaccess", "scenegraph"]


def get_all_pyside_modules():
    """
    Returns all the modules installed with PySide6
    """
    import PySide6
    # They all start with `Qt` as the prefix. Removing this prefix and getting the actual
    # module name
    return [module[2:] for module in PySide6.__all__]


from .commands import run_command, run_qmlimportscanner
from .dependency_util import find_pyside_modules, find_permission_categories, QtDependencyReader
from .nuitka_helper import Nuitka
from .config import BaseConfig, Config, DesktopConfig
from .python_helper import PythonExecutable
from .deploy_util import cleanup, finalize, create_config_file, config_option_exists
