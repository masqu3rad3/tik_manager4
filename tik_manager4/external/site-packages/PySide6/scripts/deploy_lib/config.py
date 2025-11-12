# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import sys
import configparser
import logging
import tempfile
import warnings
from configparser import ConfigParser
from pathlib import Path
from enum import Enum

from project_lib import ProjectData, DesignStudioProject, resolve_valid_project_file
from . import (DEFAULT_APP_ICON, DEFAULT_IGNORE_DIRS, find_pyside_modules,
               find_permission_categories, QtDependencyReader, run_qmlimportscanner)

# Some QML plugins like QtCore are excluded from this list as they don't contribute much to
# executable size. Excluding them saves the extra processing of checking for them in files
EXCLUDED_QML_PLUGINS = {"QtQuick", "QtQuick3D", "QtCharts", "QtWebEngine", "QtTest", "QtSensors"}

PERMISSION_MAP = {"Bluetooth": "NSBluetoothAlwaysUsageDescription:BluetoothAccess",
                  "Camera": "NSCameraUsageDescription:CameraAccess",
                  "Microphone": "NSMicrophoneUsageDescription:MicrophoneAccess",
                  "Contacts": "NSContactsUsageDescription:ContactsAccess",
                  "Calendar": "NSCalendarsUsageDescription:CalendarAccess",
                  # for iOS NSLocationWhenInUseUsageDescription and
                  # NSLocationAlwaysAndWhenInUseUsageDescription are also required.
                  "Location": "NSLocationUsageDescription:LocationAccess",
                  }


class BaseConfig:
    """Wrapper class around any .spec file with function to read and set values for the .spec file
    """

    def __init__(self, config_file: Path, comment_prefixes: str = "/",
                 existing_config_file: bool = False) -> None:
        self.config_file = config_file
        self.existing_config_file = existing_config_file
        self.parser = ConfigParser(comment_prefixes=comment_prefixes, strict=False,
                                   allow_no_value=True)
        self.parser.read(self.config_file)

    def update_config(self):
        logging.info(f"[DEPLOY] Updating config file {self.config_file}")

        # This section of code is done to preserve the formatting of the original deploy.spec
        # file where there is blank line before the comments
        with tempfile.NamedTemporaryFile('w+', delete=False) as temp_file:
            self.parser.write(temp_file, space_around_delimiters=True)
            temp_file_path = temp_file.name

        # Read the temporary file and write back to the original file with blank lines before
        # comments
        with open(temp_file_path, 'r') as temp_file, open(self.config_file, 'w') as config_file:
            previous_line = None
            for line in temp_file:
                if (line.lstrip().startswith('#') and previous_line is not None
                        and not previous_line.lstrip().startswith('#')):
                    config_file.write('\n')
                config_file.write(line)
                previous_line = line

        # Clean up the temporary file
        Path(temp_file_path).unlink()

    def set_value(self, section: str, key: str, new_value: str, raise_warning: bool = True) -> None:
        try:
            current_value = self.get_value(section, key, ignore_fail=True)
            if current_value != new_value:
                self.parser.set(section, key, new_value)
        except configparser.NoOptionError:
            if not raise_warning:
                return
            logging.warning(f"[DEPLOY] Set key '{key}': Key does not exist in section '{section}'")
        except configparser.NoSectionError:
            if not raise_warning:
                return
            logging.warning(f"[DEPLOY] Section '{section}' does not exist")

    def get_value(self, section: str, key: str, ignore_fail: bool = False) -> str | None:
        try:
            return self.parser.get(section, key)
        except configparser.NoOptionError:
            if ignore_fail:
                return None
            logging.warning(f"[DEPLOY] Get key '{key}': Key does not exist in section {section}")
        except configparser.NoSectionError:
            if ignore_fail:
                return None
            logging.warning(f"[DEPLOY] Section '{section}': does not exist")


class Config(BaseConfig):
    """
    Wrapper class around pysidedeploy.spec file, whose options are used to control the executable
    creation
    """

    def __init__(self, config_file: Path, source_file: Path, python_exe: Path, dry_run: bool,
                 existing_config_file: bool = False, extra_ignore_dirs: list[str] = None,
                 name: str = None):
        super().__init__(config_file=config_file, existing_config_file=existing_config_file)

        self.extra_ignore_dirs = extra_ignore_dirs
        self._dry_run = dry_run
        self.qml_modules = set()

        self.source_file = Path(
            self.set_or_fetch(property_value=source_file, property_key="input_file")
        ).resolve()

        self.python_path = Path(
            self.set_or_fetch(
                property_value=python_exe,
                property_key="python_path",
                property_group="python",
            )
        )

        self.title = self.set_or_fetch(property_value=name, property_key="title")

        config_icon = self.get_value("app", "icon")
        if config_icon:
            self._icon = str(Path(config_icon).resolve())
        else:
            self.icon = DEFAULT_APP_ICON

        proj_dir = self.get_value("app", "project_dir")
        if proj_dir:
            self._project_dir = Path(proj_dir).resolve()
        else:
            self.project_dir = self._find_project_dir()

        exe_directory = self.get_value("app", "exec_directory")
        if exe_directory:
            self._exe_dir = Path(exe_directory).absolute()
        else:
            self.exe_dir = self._find_exe_dir()

        self._project_file = None
        proj_file = self.get_value("app", "project_file")
        if proj_file:
            self._project_file = self.project_dir / proj_file
        else:
            proj_file = self._find_project_file()
            if proj_file:
                self.project_file = proj_file

        self.project_data = None
        if self.project_file and self.project_file.exists():
            self.project_data = ProjectData(project_file=self.project_file)

        self._qml_files = []
        # Design Studio projects include the qml files using Qt resources
        if source_file and not DesignStudioProject.is_ds_project(source_file):
            config_qml_files = self.get_value("qt", "qml_files")
            if config_qml_files and self.project_dir and self.existing_config_file:
                self._qml_files = [Path(self.project_dir)
                                   / file for file in config_qml_files.split(",")]
            else:
                self.qml_files = self._find_qml_files()

        self._excluded_qml_plugins = []
        excl_qml_plugins = self.get_value("qt", "excluded_qml_plugins")
        if excl_qml_plugins and self.existing_config_file:
            self._excluded_qml_plugins = excl_qml_plugins.split(",")
        else:
            self.excluded_qml_plugins = self._find_excluded_qml_plugins()

        self._generated_files_path = self.source_file.parent / "deployment"

        self.modules = []

    def set_or_fetch(self, property_value, property_key, property_group="app") -> str:
        """
        If a new property value is provided, store it in the config file
        Otherwise return the existing value in the config file.
        Raise an exception if neither are available.

        :param property_value: The value to set if provided.
        :param property_key: The configuration key.
        :param property_group: The configuration group (default is "app").
        :return: The configuration value.
        :raises RuntimeError: If no value is provided and no existing value is found.
        """
        existing_value = self.get_value(property_group, property_key)

        if property_value:
            self.set_value(property_group, property_key, str(property_value))
            return property_value
        if existing_value:
            return existing_value

        raise RuntimeError(
            f"[DEPLOY] No value for {property_key} specified in config file or as cli option"
        )

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @property
    def generated_files_path(self) -> Path:
        return self._generated_files_path

    @property
    def qml_files(self) -> list[Path]:
        return self._qml_files

    @qml_files.setter
    def qml_files(self, qml_files: list[Path]):
        self._qml_files = qml_files
        qml_files = [str(file.absolute().relative_to(self.project_dir.absolute()))
                     if file.absolute().is_relative_to(self.project_dir) else str(file.absolute())
                     for file in self.qml_files]
        qml_files.sort()
        self.set_value("qt", "qml_files", ",".join(qml_files))

    @property
    def project_dir(self) -> Path:
        return self._project_dir

    @project_dir.setter
    def project_dir(self, project_dir: Path) -> None:
        rel_path = (
            project_dir.relative_to(self.config_file.parent)
            if project_dir.is_relative_to(self.config_file.parent)
            else project_dir
        )
        self._project_dir = project_dir
        self.set_value("app", "project_dir", str(rel_path))

    @property
    def project_file(self) -> Path:
        return self._project_file

    @project_file.setter
    def project_file(self, project_file: Path):
        self._project_file = project_file
        self.set_value("app", "project_file", str(project_file.relative_to(self.project_dir)))

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, icon: str):
        self._icon = icon
        self.set_value("app", "icon", icon)

    @property
    def source_file(self) -> Path:
        return self._source_file

    @source_file.setter
    def source_file(self, source_file: Path) -> None:
        rel_path = (
            source_file.relative_to(self.config_file.parent)
            if source_file.is_relative_to(self.config_file.parent)
            else source_file
        )
        self._source_file = source_file
        self.set_value("app", "input_file", str(rel_path))

    @property
    def python_path(self) -> Path:
        return self._python_path

    @python_path.setter
    def python_path(self, python_path: Path):
        self._python_path = python_path

    @property
    def extra_args(self) -> str:
        return self.get_value("nuitka", "extra_args")

    @extra_args.setter
    def extra_args(self, extra_args: str):
        self.set_value("nuitka", "extra_args", extra_args)

    @property
    def excluded_qml_plugins(self) -> list[str]:
        return self._excluded_qml_plugins

    @excluded_qml_plugins.setter
    def excluded_qml_plugins(self, excluded_qml_plugins: list[str]):
        self._excluded_qml_plugins = excluded_qml_plugins
        if excluded_qml_plugins:  # check required for Android
            excluded_qml_plugins.sort()
            self.set_value("qt", "excluded_qml_plugins", ",".join(excluded_qml_plugins))

    @property
    def exe_dir(self) -> Path:
        return self._exe_dir

    @exe_dir.setter
    def exe_dir(self, exe_dir: Path):
        self._exe_dir = exe_dir
        self.set_value("app", "exec_directory", str(exe_dir))

    @property
    def modules(self) -> list[str]:
        return self._modules

    @modules.setter
    def modules(self, modules: list[str]):
        self._modules = modules
        modules.sort()
        self.set_value("qt", "modules", ",".join(modules))

    def _find_qml_files(self):
        """
        Fetches all the qml_files in the folder and sets them if the
        field qml_files is empty in the config_file
        """

        if self.project_data:
            qml_files = [(self.project_dir / str(qml_file)) for qml_file in
                         self.project_data.qml_files]
            for sub_project_file in self.project_data.sub_projects_files:
                qml_files.extend([self.project_dir / str(qml_file) for qml_file in
                                  ProjectData(project_file=sub_project_file).qml_files])
        else:
            # Filter out files from DEFAULT_IGNORE_DIRS
            qml_files = [
                file for file in self.project_dir.glob("**/*.qml")
                if all(part not in file.parts for part in DEFAULT_IGNORE_DIRS)
            ]

            if len(qml_files) > 500:
                warnings.warn(
                    "You seem to include a lot of QML files from "
                    f"{self.project_dir}. This can lead to errors in deployment."
                )

        return qml_files

    def _find_project_dir(self) -> Path:
        if DesignStudioProject.is_ds_project(self.source_file):
            return DesignStudioProject(self.source_file).project_dir

        # There is no other way to find the project_dir than assume it is the parent directory
        # of source_file
        return self.source_file.parent

    def _find_project_file(self) -> Path | None:
        if not self.source_file:
            raise RuntimeError("[DEPLOY] Source file not set in config file")

        if DesignStudioProject.is_ds_project(self.source_file):
            pyproject_location = self.source_file.parent
        else:
            pyproject_location = self.project_dir

        try:
            return resolve_valid_project_file(pyproject_location)
        except ValueError as e:
            logging.warning(f"[DEPLOY] Unable to resolve a valid project file. Proceeding without a"
                            f" project file. Details:\n{e}.")
        return None

    def _find_excluded_qml_plugins(self) -> list[str] | None:
        if not self.qml_files and not DesignStudioProject.is_ds_project(self.source_file):
            return None

        self.qml_modules = set(run_qmlimportscanner(project_dir=self.project_dir,
                                                    dry_run=self.dry_run))
        excluded_qml_plugins = EXCLUDED_QML_PLUGINS.difference(self.qml_modules)

        # sorting needed for dry_run testing
        return sorted(excluded_qml_plugins)

    def _find_exe_dir(self) -> Path:
        if self.project_dir == Path.cwd():
            return self.project_dir.relative_to(Path.cwd())

        return self.project_dir

    def _find_pysidemodules(self) -> list[str]:
        modules = find_pyside_modules(project_dir=self.project_dir,
                                      extra_ignore_dirs=self.extra_ignore_dirs,
                                      project_data=self.project_data)
        logging.info("The following PySide modules were found from the Python files of "
                     f"the project {modules}")
        return modules

    def _find_qtquick_modules(self) -> list[str]:
        """Identify if QtQuick is used in QML files and add them as dependency
        """
        extra_modules = []
        if not self.qml_modules and self.qml_files:
            self.qml_modules = set(run_qmlimportscanner(project_dir=self.project_dir,
                                                        dry_run=self.dry_run))

        if "QtQuick" in self.qml_modules:
            extra_modules.append("Quick")

        if "QtQuick.Controls" in self.qml_modules:
            extra_modules.append("QuickControls2")

        return extra_modules


class DesktopConfig(Config):
    """Wrapper class around pysidedeploy.spec, but specific to Desktop deployment
    """

    class NuitkaMode(Enum):
        ONEFILE = "onefile"
        STANDALONE = "standalone"

    def __init__(self, config_file: Path, source_file: Path, python_exe: Path, dry_run: bool,
                 existing_config_file: bool = False, extra_ignore_dirs: list[str] = None,
                 mode: str = "onefile", name: str = None):
        super().__init__(config_file, source_file, python_exe, dry_run, existing_config_file,
                         extra_ignore_dirs, name=name)
        self.dependency_reader = QtDependencyReader(dry_run=self.dry_run)
        modules = self.get_value("qt", "modules")
        if modules:
            self._modules = modules.split(",")
        else:
            modules = self._find_pysidemodules()
            modules += self._find_qtquick_modules()
            modules += self._find_dependent_qt_modules(modules=modules)
            # remove duplicates
            self.modules = list(set(modules))

        self._qt_plugins = []
        if self.get_value("qt", "plugins"):
            self._qt_plugins = self.get_value("qt", "plugins").split(",")
        else:
            self.qt_plugins = self.dependency_reader.find_plugin_dependencies(self.modules,
                                                                              python_exe)

        self._permissions = []
        if sys.platform == "darwin":
            nuitka_macos_permissions = self.get_value("nuitka", "macos.permissions")
            if nuitka_macos_permissions:
                self._permissions = nuitka_macos_permissions.split(",")
            else:
                self.permissions = self._find_permissions()

        self._mode = self.NuitkaMode.ONEFILE
        if self.get_value("nuitka", "mode") == self.NuitkaMode.STANDALONE.value:
            self._mode = self.NuitkaMode.STANDALONE
        elif mode == self.NuitkaMode.STANDALONE.value:
            self.mode = self.NuitkaMode.STANDALONE

        if DesignStudioProject.is_ds_project(self.source_file):
            ds_project = DesignStudioProject(self.source_file)
            if not ds_project.compiled_resources_available():
                raise RuntimeError(f"[DEPLOY] Compiled resources file not found: "
                                   f"{ds_project.compiled_resources_file.absolute()}. "
                                   f"Build the project using 'pyside6-project build' or compile "
                                   f"the resources manually using pyside6-rcc")

    @property
    def qt_plugins(self) -> list[str]:
        return self._qt_plugins

    @qt_plugins.setter
    def qt_plugins(self, qt_plugins: list[str]):
        self._qt_plugins = qt_plugins
        qt_plugins.sort()
        self.set_value("qt", "plugins", ",".join(qt_plugins))

    @property
    def permissions(self) -> list[str]:
        return self._permissions

    @permissions.setter
    def permissions(self, permissions: list[str]):
        self._permissions = permissions
        permissions.sort()
        self.set_value("nuitka", "macos.permissions", ",".join(permissions))

    @property
    def mode(self) -> NuitkaMode:
        return self._mode

    @mode.setter
    def mode(self, mode: NuitkaMode):
        self._mode = mode
        self.set_value("nuitka", "mode", mode.value)

    def _find_dependent_qt_modules(self, modules: list[str]) -> list[str]:
        """
        Given pysidedeploy_config.modules, find all the other dependent Qt modules.
        """
        all_modules = set(modules)

        if not self.dependency_reader.lib_reader:
            warnings.warn(f"[DEPLOY] Unable to find {self.dependency_reader.lib_reader_name}. This "
                          f"tool helps to find the Qt module dependencies of the application. "
                          f"Skipping checking for dependencies.", category=RuntimeWarning)
            return []

        for module_name in modules:
            self.dependency_reader.find_dependencies(module=module_name, used_modules=all_modules)

        return list(all_modules)

    def _find_permissions(self) -> list[str]:
        """
        Finds and sets the usage description string required for each permission requested by the
        macOS application.
        """
        permissions = []
        perm_categories = find_permission_categories(project_dir=self.project_dir,
                                                     extra_ignore_dirs=self.extra_ignore_dirs,
                                                     project_data=self.project_data)

        perm_categories_str = ",".join(perm_categories)
        logging.info(f"[DEPLOY] Usage descriptions for the {perm_categories_str} will be added to "
                     "the Info.plist file of the macOS application bundle")

        # Handling permissions
        for perm_category in perm_categories:
            if perm_category in PERMISSION_MAP:
                permissions.append(PERMISSION_MAP[perm_category])

        return permissions
