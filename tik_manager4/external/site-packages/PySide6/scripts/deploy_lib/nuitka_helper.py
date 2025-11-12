# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

# enables to use typehints for classes that has not been defined yet or imported
# used for resolving circular imports
from __future__ import annotations
import logging
import os
import shlex
import sys
from pathlib import Path

from project_lib import DesignStudioProject
from . import MAJOR_VERSION, run_command, DEFAULT_IGNORE_DIRS, PLUGINS_TO_REMOVE
from .config import DesktopConfig


class Nuitka:
    """
    Wrapper class around the nuitka executable, enabling its usage through python code
    """

    def __init__(self, nuitka):
        self.nuitka = nuitka
        # plugins to ignore. The sensible plugins are include by default by Nuitka for PySide6
        # application deployment
        self.qt_plugins_to_ignore = ["imageformats",  # being Nuitka `sensible`` plugins
                                     "iconengines",
                                     "mediaservice",
                                     "printsupport",
                                     "platforms",
                                     "platformthemes",
                                     "styles",
                                     "wayland-shell-integration",
                                     "wayland-decoration-client",
                                     "wayland-graphics-integration-client",
                                     "egldeviceintegrations",
                                     "xcbglintegrations",
                                     "tls",  # end Nuitka `sensible` plugins
                                     "generic"  # plugins that error with Nuitka
                                     ]

        self.files_to_ignore = [".cpp.o", ".qsb"]

    @staticmethod
    def icon_option():
        if sys.platform == "linux":
            return "--linux-icon"
        elif sys.platform == "win32":
            return "--windows-icon-from-ico"
        else:
            return "--macos-app-icon"

    def _create_windows_command(self, source_file: Path, command: list):
        """
        Special case for Windows where the command length is limited to 8191 characters.
        """

        # if the platform is windows and the command is more than 8191 characters, the command
        # will fail with the error message "The command line is too long". To avoid this, we will
        # we will move the source_file to the intermediate source file called deploy_main.py, and
        # include the Nuitka options direcly in the main file as mentioned in
        # https://nuitka.net/user-documentation/user-manual.html#nuitka-project-options

        # convert command into a format recognized by Nuitka when written to the main file
        # the first item is ignore because it is 'python -m nuitka'
        nuitka_comment_options = []
        for command_entry in command[4:]:
            nuitka_comment_options.append(f"# nuitka-project: {command_entry}")
        nuitka_comment_options_str = "\n".join(nuitka_comment_options)
        nuitka_comment_options_str += "\n"

        # read the content of the source file
        new_source_content = (nuitka_comment_options_str
                              + Path(source_file).read_text(encoding="utf-8"))

        # create and write back the new source content to deploy_main.py
        new_source_file = source_file.parent / "deploy_main.py"
        new_source_file.write_text(new_source_content, encoding="utf-8")

        return new_source_file

    def create_executable(self, source_file: Path, extra_args: str, qml_files: list[Path],
                          qt_plugins: list[str], excluded_qml_plugins: list[str], icon: str,
                          dry_run: bool, permissions: list[str],
                          mode: DesktopConfig.NuitkaMode) -> str:
        qt_plugins = [plugin for plugin in qt_plugins if plugin not in self.qt_plugins_to_ignore]
        extra_args = shlex.split(extra_args)

        # macOS uses the --standalone option by default to create an app bundle
        if sys.platform == "darwin":
            # create an app bundle
            extra_args.extend(["--standalone", "--macos-create-app-bundle"])
            permission_pattern = "--macos-app-protected-resource={permission}"
            for permission in permissions:
                extra_args.append(permission_pattern.format(permission=permission))
        else:
            extra_args.append(f"--{mode.value}")

        qml_args = []
        if qml_files:
            # include all the subdirectories in the project directory as data directories
            # This includes all the qml modules
            all_relevant_subdirs = []
            for subdir in source_file.parent.iterdir():
                if subdir.is_dir() and subdir.name not in DEFAULT_IGNORE_DIRS:
                    extra_args.append(f"--include-data-dir={subdir}="
                                      f"./{subdir.name}")
                    all_relevant_subdirs.append(subdir)

            # find all the qml files that are not included via the data directories
            extra_qml_files = [file for file in qml_files
                               if file.parent not in all_relevant_subdirs]

            # This will generate options for each file using:
            #     --include-data-files=ABSOLUTE_PATH_TO_FILE=RELATIVE_PATH_TO ROOT
            # for each file.
            qml_args.extend(
                [f"--include-data-files={qml_file.resolve()}="
                    f"./{qml_file.resolve().relative_to(source_file.resolve().parent)}"
                    for qml_file in extra_qml_files]
            )

        if qml_files or DesignStudioProject.is_ds_project(source_file):
            # add qml plugin. The `qml`` plugin name is not present in the module json files shipped
            # with Qt and hence not in `qt_plugins``. However, Nuitka uses the 'qml' plugin name to
            # include the necessary qml plugins. There we have to add it explicitly for a qml
            # application
            qt_plugins.append("qml")

            if excluded_qml_plugins:
                prefix = "lib" if sys.platform != "win32" else ""
                for plugin in excluded_qml_plugins:
                    dll_name = plugin.replace("Qt", f"Qt{MAJOR_VERSION}")
                    qml_args.append(f"--noinclude-dlls={prefix}{dll_name}*")

            # Exclude .qen json files from QtQuickEffectMaker
            # These files are not relevant for PySide6 applications
            qml_args.append("--noinclude-dlls=*/qml/QtQuickEffectMaker/*")

        # Exclude files that cannot be processed by Nuitka
        for file in self.files_to_ignore:
            extra_args.append(f"--noinclude-dlls=*{file}")

        output_dir = source_file.parent / "deployment"
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.info("[DEPLOY] Running Nuitka")
        command = self.nuitka + [
            os.fspath(source_file),
            "--follow-imports",
            "--enable-plugin=pyside6",
            f"--output-dir={output_dir}",
        ]

        command.extend(extra_args + qml_args)
        command.append(f"{self.__class__.icon_option()}={icon}")
        if qt_plugins:
            # sort qt_plugins so that the result is definitive when testing
            qt_plugins.sort()
            # remove the following plugins from the qt_plugins list as Nuitka only checks
            # for plugins within PySide6/Qt/plugins folder, and the following plugins
            # are not present in the PySide6/Qt/plugins folder
            qt_plugins = [plugin for plugin in qt_plugins if plugin not in PLUGINS_TO_REMOVE]
            qt_plugins_str = ",".join(qt_plugins)
            command.append(f"--include-qt-plugins={qt_plugins_str}")

        long_command = False
        if sys.platform == "win32" and len(" ".join(str(cmd) for cmd in command)) > 7000:
            logging.info("[DEPLOY] Nuitka command too long for Windows. "
                         "Copying the contents of main Python file to an intermediate "
                         "deploy_main.py file")
            long_command = True
            new_source_file = self._create_windows_command(source_file=source_file, command=command)
            command = self.nuitka + [os.fspath(new_source_file)]

        command_str, _ = run_command(command=command, dry_run=dry_run)

        # if deploy_main.py exists, delete it after the command is run
        if long_command:
            os.remove(source_file.parent / "deploy_main.py")

        return command_str
