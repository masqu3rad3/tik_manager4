# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import ast
import re
import os
import site
import json
import warnings
import logging
import shutil
import sys
from pathlib import Path
from functools import lru_cache

from . import IMPORT_WARNING_PYSIDE, DEFAULT_IGNORE_DIRS, run_command


@lru_cache(maxsize=None)
def get_py_files(project_dir: Path, extra_ignore_dirs: tuple[Path] = None, project_data=None):
    """Finds and returns all the Python files in the project
    """
    py_candidates = []
    ignore_dirs = DEFAULT_IGNORE_DIRS.copy()

    if project_data:
        py_candidates = project_data.python_files
        ui_candidates = project_data.ui_files
        qrc_candidates = project_data.qrc_files

        def add_uic_qrc_candidates(candidates, candidate_type):
            possible_py_candidates = []
            missing_files = []
            for file in candidates:
                py_file = file.parent / f"{candidate_type}_{file.stem}.py"
                if py_file.exists():
                    possible_py_candidates.append(py_file)
                else:
                    missing_files.append((str(file), str(py_file)))

            if missing_files:
                missing_details = "\n".join(
                    f"{candidate_type.upper()} file: {src} -> Missing Python file: {dst}"
                    for src, dst in missing_files
                )
                warnings.warn(
                    f"[DEPLOY] The following {candidate_type} files do not have corresponding "
                    f"Python files:\n {missing_details}",
                    category=RuntimeWarning
                )

            py_candidates.extend(possible_py_candidates)

        if ui_candidates:
            add_uic_qrc_candidates(ui_candidates, "ui")

        if qrc_candidates:
            add_uic_qrc_candidates(qrc_candidates, "rc")

        return py_candidates

    # incase there is not .pyproject file, search all python files in project_dir, except
    # ignore_dirs
    if extra_ignore_dirs:
        ignore_dirs.update(extra_ignore_dirs)

    # find relevant .py files
    _walk = os.walk(project_dir)
    for root, dirs, files in _walk:
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for py_file in files:
            if py_file.endswith(".py"):
                py_candidates.append(Path(root) / py_file)

    return py_candidates


@lru_cache(maxsize=None)
def get_ast(py_file: Path):
    """Given a Python file returns the abstract syntax tree
    """
    contents = py_file.read_text(encoding="utf-8")
    try:
        tree = ast.parse(contents)
    except SyntaxError:
        print(f"[DEPLOY] Unable to parse {py_file}")
    return tree


def find_permission_categories(project_dir: Path, extra_ignore_dirs: list[Path] = None,
                               project_data=None):
    """Given the project directory, finds all the permission categories required by the
    project. eg: Camera, Bluetooth, Contacts etc.

    Note: This function is only relevant for mac0S deployment.
    """
    all_perm_categories = set()
    mod_pattern = re.compile("Q(?P<mod_name>.*)Permission")

    def pyside_permission_imports(py_file: Path):
        perm_categories = []
        try:
            tree = get_ast(py_file)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    main_mod_name = node.module
                    if main_mod_name == "PySide6.QtCore":
                        # considers 'from PySide6.QtCore import QtMicrophonePermission'
                        for imported_module in node.names:
                            full_mod_name = imported_module.name
                            match = mod_pattern.search(full_mod_name)
                            if match:
                                mod_name = match.group("mod_name")
                                perm_categories.append(mod_name)
                        continue

                if isinstance(node, ast.Import):
                    for imported_module in node.names:
                        full_mod_name = imported_module.name
                        if full_mod_name == "PySide6":
                            logging.warning(IMPORT_WARNING_PYSIDE.format(str(py_file)))
        except Exception as e:
            raise RuntimeError(f"[DEPLOY] Finding permission categories failed on file "
                               f"{str(py_file)} with error {e}")

        return set(perm_categories)

    if extra_ignore_dirs is not None:
        extra_ignore_dirs = tuple(extra_ignore_dirs)
    py_candidates = get_py_files(project_dir, extra_ignore_dirs, project_data)
    for py_candidate in py_candidates:
        all_perm_categories = all_perm_categories.union(pyside_permission_imports(py_candidate))

    if not all_perm_categories:
        ValueError("[DEPLOY] No permission categories were found for macOS app bundle creation.")

    return all_perm_categories


def find_pyside_modules(project_dir: Path, extra_ignore_dirs: list[Path] = None,
                        project_data=None):
    """
    Searches all the python files in the project to find all the PySide modules used by
    the application.
    """
    all_modules = set()
    mod_pattern = re.compile("PySide6.Qt(?P<mod_name>.*)")

    @lru_cache
    def pyside_module_imports(py_file: Path):
        modules = []
        try:
            tree = get_ast(py_file)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    main_mod_name = node.module
                    if main_mod_name and main_mod_name.startswith("PySide6"):
                        if main_mod_name == "PySide6":
                            # considers 'from PySide6 import QtCore'
                            for imported_module in node.names:
                                full_mod_name = imported_module.name
                                if full_mod_name.startswith("Qt"):
                                    modules.append(full_mod_name[2:])
                            continue

                        # considers 'from PySide6.QtCore import Qt'
                        match = mod_pattern.search(main_mod_name)
                        if match:
                            mod_name = match.group("mod_name")
                            modules.append(mod_name)
                        else:
                            logging.warning((
                                f"[DEPLOY] Unable to find module name from {ast.dump(node)}"))

                if isinstance(node, ast.Import):
                    for imported_module in node.names:
                        full_mod_name = imported_module.name
                        if full_mod_name == "PySide6":
                            logging.warning(IMPORT_WARNING_PYSIDE.format(str(py_file)))
        except Exception as e:
            raise RuntimeError(f"[DEPLOY] Finding module import failed on file {str(py_file)} with "
                               f"error {e}")

        return set(modules)

    if extra_ignore_dirs is not None:
        extra_ignore_dirs = tuple(extra_ignore_dirs)
    py_candidates = get_py_files(project_dir, extra_ignore_dirs, project_data)
    for py_candidate in py_candidates:
        all_modules = all_modules.union(pyside_module_imports(py_candidate))

    if not all_modules:
        ValueError("[DEPLOY] No PySide6 modules were found")

    return list(all_modules)


class QtDependencyReader:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.lib_reader_name = None
        self.qt_module_path_pattern = None
        self.lib_pattern = None
        self.command = None
        self.qt_libs_dir = None

        if sys.platform == "linux":
            self.lib_reader_name = "readelf"
            self.qt_module_path_pattern = "libQt6{module}.so.6"
            self.lib_pattern = re.compile("libQt6(?P<mod_name>.*).so.6")
            self.command_args = "-d"
        elif sys.platform == "darwin":
            self.lib_reader_name = "dyld_info"
            self.qt_module_path_pattern = "Qt{module}.framework/Versions/A/Qt{module}"
            self.lib_pattern = re.compile("@rpath/Qt(?P<mod_name>.*).framework/Versions/A/")
            self.command_args = "-dependents"
        elif sys.platform == "win32":
            self.lib_reader_name = "dumpbin"
            self.qt_module_path_pattern = "Qt6{module}.dll"
            self.lib_pattern = re.compile("Qt6(?P<mod_name>.*).dll")
            self.command_args = "/dependents"
        else:
            print(f"[DEPLOY] Deployment on unsupported platfrom {sys.platform}")
            sys.exit(1)

        self.pyside_install_dir = None
        self.qt_libs_dir = self.get_qt_libs_dir()
        self._lib_reader = shutil.which(self.lib_reader_name)

    def get_qt_libs_dir(self):
        """
        Finds the path to the Qt libs directory inside PySide6 package installation
        """
        # PYSIDE-2785 consider dist-packages for Debian based systems
        for possible_site_package in site.getsitepackages():
            if possible_site_package.endswith(("site-packages", "dist-packages")):
                self.pyside_install_dir = Path(possible_site_package) / "PySide6"
                if self.pyside_install_dir.exists():
                    break

        if not self.pyside_install_dir:
            print("Unable to find where PySide6 is installed. Exiting ...")
            sys.exit(-1)

        if sys.platform == "win32":
            return self.pyside_install_dir

        return self.pyside_install_dir / "Qt" / "lib"  # for linux and macOS

    @property
    def lib_reader(self):
        return self._lib_reader

    def find_dependencies(self, module: str, used_modules: set[str] = None):
        """
        Given a Qt module, find all the other Qt modules it is dependent on and add it to the
        'used_modules' set
        """
        qt_module_path = self.qt_libs_dir / self.qt_module_path_pattern.format(module=module)
        if not qt_module_path.exists():
            warnings.warn(f"[DEPLOY] {qt_module_path.name} not found in {str(qt_module_path)}."
                          "Skipping finding its dependencies.", category=RuntimeWarning)
            return

        lib_pattern = re.compile(self.lib_pattern)
        command = [self.lib_reader, self.command_args, str(qt_module_path)]
        # print the command if dry_run is True.
        # Normally run_command is going to print the command in dry_run mode. But, this is a
        # special case where we need to print the command as well as to run it.
        if self.dry_run:
            command_str = " ".join(command)
            print(command_str + "\n")

        # We need to run this even for dry run, to see the full Nuitka command being executed
        _, output = run_command(command=command, dry_run=False, fetch_output=True)

        dependent_modules = set()
        for line in output.splitlines():
            line = line.decode("utf-8").lstrip()
            if sys.platform == "darwin":
                if line.endswith(f"Qt{module} [arm64]:"):
                    # macOS Qt frameworks bundles have both x86_64 and arm64 architectures
                    # We only need to consider one as the dependencies are redundant
                    break
                elif line.endswith(f"Qt{module} [X86_64]:"):
                    # this line needs to be skipped because it matches with the pattern
                    # and is related to the module itself, not the dependencies of the module
                    continue
            elif sys.platform == "win32" and line.startswith("Summary"):
                # the dependencies would be found before the `Summary` line
                break
            match = lib_pattern.search(line)
            if match:
                dep_module = match.group("mod_name")
                dependent_modules.add(dep_module)
                if dep_module not in used_modules:
                    used_modules.add(dep_module)
                    self.find_dependencies(module=dep_module, used_modules=used_modules)

        if dependent_modules:
            logging.info(f"[DEPLOY] Following dependencies found for {module}: {dependent_modules}")
        else:
            logging.info(f"[DEPLOY] No Qt dependencies found for {module}")

    def find_plugin_dependencies(self, used_modules: list[str], python_exe: Path) -> list[str]:
        """
        Given the modules used by the application, returns all the required plugins
        """
        plugins = set()
        pyside_wheels = ["PySide6_Essentials", "PySide6_Addons"]
        # TODO from 3.12 use list(dist.name for dist in importlib.metadata.distributions())
        _, installed_packages = run_command(command=[str(python_exe), "-m", "pip", "freeze"],
                                            dry_run=False, fetch_output=True)
        installed_packages = [p.decode().split('==')[0] for p in installed_packages.split()]
        for pyside_wheel in pyside_wheels:
            if pyside_wheel not in installed_packages:
                # the wheel is not installed and hence no plugins are checked for its modules
                logging.warning((f"[DEPLOY] The package {pyside_wheel} is not installed. "))
                continue
            pyside_mod_plugin_json_name = f"{pyside_wheel}.json"
            pyside_mod_plugin_json_file = self.pyside_install_dir / pyside_mod_plugin_json_name
            if not pyside_mod_plugin_json_file.exists():
                warnings.warn(f"[DEPLOY] Unable to find {pyside_mod_plugin_json_file}.",
                              category=RuntimeWarning)
                continue

            # convert the json to dict
            pyside_mod_dict = {}
            with open(pyside_mod_plugin_json_file) as pyside_json:
                pyside_mod_dict = json.load(pyside_json)

            # find all the plugins in the modules
            for module in used_modules:
                plugins.update(pyside_mod_dict.get(module, []))

        return list(plugins)
