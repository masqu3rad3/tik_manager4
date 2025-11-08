# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from . import EXE_FORMAT
from .config import Config, DesktopConfig


def config_option_exists():
    for argument in sys.argv:
        if any(item in argument for item in ["--config-file", "-c"]):
            return True

    return False


def cleanup(config: Config, is_android: bool = False):
    """
    Cleanup the generated build folders/files.

    Parameters:
    config (Config): The configuration object containing paths and settings.
    is_android (bool): Flag indicating if the cleanup is for an Android project. Default is False.
    """
    if config.generated_files_path.exists():
        try:
            shutil.rmtree(config.generated_files_path)
            logging.info("[DEPLOY] Deployment directory purged")
        except PermissionError as e:
            print(f"{type(e).__name__}: {e}")
            logging.warning(f"[DEPLOY] Could not delete {config.generated_files_path}")

    if is_android:
        buildozer_spec: Path = config.project_dir / "buildozer.spec"
        if buildozer_spec.exists():
            try:
                buildozer_spec.unlink()
                logging.info(f"[DEPLOY] {str(buildozer_spec)} removed")
            except PermissionError as e:
                print(f"{type(e).__name__}: {e}")
                logging.warning(f"[DEPLOY] Could not delete {buildozer_spec}")

        buildozer_build: Path = config.project_dir / ".buildozer"
        if buildozer_build.exists():
            try:
                shutil.rmtree(buildozer_build)
                logging.info(f"[DEPLOY] {str(buildozer_build)} removed")
            except PermissionError as e:
                print(f"{type(e).__name__}: {e}")
                logging.warning(f"[DEPLOY] Could not delete {buildozer_build}")


def create_config_file(main_file: Path, dry_run: bool = False):
    """
        Creates a new pysidedeploy.spec
    """

    config_file = main_file.parent / "pysidedeploy.spec"
    logging.info(f"[DEPLOY] Creating config file {config_file}")

    default_config_file = Path(__file__).parent / "default.spec"
    # the config parser needs a reference to parse. So, in the case of --dry-run
    # use the default.spec file.
    if dry_run:
        return default_config_file

    shutil.copy(default_config_file, config_file)
    return config_file


def finalize(config: DesktopConfig):
    """
        Copy the executable into the final location
        For Android deployment, this is done through buildozer
    """
    exe_format = EXE_FORMAT
    if config.mode == DesktopConfig.NuitkaMode.STANDALONE and sys.platform != "darwin":
        exe_format = ".dist"

    generated_exec_path = config.generated_files_path / (config.source_file.stem + exe_format)
    if not generated_exec_path.exists():
        logging.error(f"[DEPLOY] Executable not found at {generated_exec_path.absolute()}")
        return

    logging.info(f"[DEPLOY] executable generated at {generated_exec_path.absolute()}")
    if not config.exe_dir:
        logging.info("[DEPLOY] Not copying output executable because no output directory specified")
        return

    output_path = config.exe_dir / (config.title + exe_format)

    if sys.platform == "darwin" or config.mode == DesktopConfig.NuitkaMode.STANDALONE:
        # Copy the folder that contains the executable
        logging.info(f"[DEPLOY] copying generated folder to {output_path.absolute()}")
        shutil.copytree(generated_exec_path, output_path, dirs_exist_ok=True)
    else:
        # Copy a single file
        logging.info(f"[DEPLOY] copying generated file to {output_path.absolute()}")
        shutil.copy(generated_exec_path, output_path)

    print(f"[DEPLOY] Executed file created in {output_path.absolute()}")
