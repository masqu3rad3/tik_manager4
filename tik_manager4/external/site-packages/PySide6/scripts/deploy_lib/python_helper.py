# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import logging
import os
import sys

from importlib import util
from importlib.metadata import version
from pathlib import Path

from . import Config, run_command


class PythonExecutable:
    """
    Wrapper class around Python executable
    """

    def __init__(self, python_path: Path = None, dry_run: bool = False, init: bool = False,
                 force: bool = False):

        self.dry_run = dry_run
        self.init = init
        if not python_path:
            response = "yes"
            # checking if inside virtual environment
            if not self.is_venv() and not force and not self.dry_run and not self.init:
                response = input(("You are not using a virtual environment. pyside6-deploy needs "
                                  "to install a few Python packages for deployment to work "
                                  "seamlessly. \n Proceed? [Y/n]"))

            if response.lower() in ["no", "n"]:
                print("[DEPLOY] Exiting ...")
                sys.exit(0)

            self.exe = Path(sys.executable)
        else:
            self.exe = python_path

        logging.info(f"[DEPLOY] Using Python at {str(self.exe)}")

    @property
    def exe(self):
        return Path(self._exe)

    @exe.setter
    def exe(self, exe):
        self._exe = exe

    @staticmethod
    def is_venv():
        venv = os.environ.get("VIRTUAL_ENV")
        return True if venv else False

    def is_pyenv_python(self):
        pyenv_root = os.environ.get("PYENV_ROOT")

        if pyenv_root:
            resolved_exe = self.exe.resolve()
            if str(resolved_exe).startswith(pyenv_root):
                return True

        return False

    def install(self, packages: list = None):
        _, installed_packages = run_command(command=[str(self.exe), "-m", "pip", "freeze"],
                                            dry_run=False, fetch_output=True)
        installed_packages = [p.decode().split('==')[0] for p in installed_packages.split()]
        for package in packages:
            package_info = package.split('==')
            package_components_len = len(package_info)
            package_name, package_version = None, None
            if package_components_len == 1:
                package_name = package_info[0]
            elif package_components_len == 2:
                package_name = package_info[0]
                package_version = package_info[1]
            else:
                raise ValueError(f"{package} should be of the format 'package_name'=='version'")
            if (package_name not in installed_packages) and (not self.is_installed(package_name)):
                logging.info(f"[DEPLOY] Installing package: {package}")
                run_command(
                    command=[self.exe, "-m", "pip", "install", package],
                    dry_run=self.dry_run,
                )
            elif package_version:
                installed_version = version(package_name)
                if package_version != installed_version:
                    logging.info(f"[DEPLOY] Installing package: {package_name}"
                                 f"version: {package_version}")
                    run_command(
                        command=[self.exe, "-m", "pip", "install", "--force", package],
                        dry_run=self.dry_run,
                    )
                else:
                    logging.info(f"[DEPLOY] package: {package_name}=={package_version}"
                                 " already installed")
            else:
                logging.info(f"[DEPLOY] package: {package_name} already installed")

    def is_installed(self, package):
        return bool(util.find_spec(package))

    def install_dependencies(self, config: Config, packages: str, is_android: bool = False):
        """
        Installs the python package dependencies for the target deployment platform
        """
        packages = config.get_value("python", packages).split(",")
        if not self.init:
            # install packages needed for deployment
            logging.info("[DEPLOY] Installing dependencies")
            self.install(packages=packages)
            # nuitka requires patchelf to make patchelf rpath changes for some Qt files
            if sys.platform.startswith("linux") and not is_android:
                self.install(packages=["patchelf"])
        elif is_android:
            # install only buildozer
            logging.info("[DEPLOY] Installing buildozer")
            buildozer_package_with_version = ([package for package in packages
                                               if package.startswith("buildozer")])
            self.install(packages=list(buildozer_package_with_version))
