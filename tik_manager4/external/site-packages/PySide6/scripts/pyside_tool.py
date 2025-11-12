#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import importlib
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

import PySide6 as ref_mod

VIRTUAL_ENV = "VIRTUAL_ENV"


def is_pyenv_python():
    pyenv_root = os.environ.get("PYENV_ROOT")

    if pyenv_root:
        resolved_exe = Path(sys.executable).resolve()
        if str(resolved_exe).startswith(pyenv_root):
            return True

    return False


def is_virtual_env():
    return sys.prefix != sys.base_prefix


def init_virtual_env():
    """PYSIDE-2251: Enable running from a non-activated virtual environment
       as is the case for Visual Studio Code by setting the VIRTUAL_ENV
       variable which is used by the Qt Designer plugin."""
    if is_virtual_env() and not os.environ.get(VIRTUAL_ENV):
        os.environ[VIRTUAL_ENV] = sys.prefix


def main():
    # This will take care of "pyside6-lupdate" listed as an entrypoint
    # in setup.py are copied to 'scripts/..'
    cmd = os.path.join("..", os.path.basename(sys.argv[0]))
    command = [os.path.join(os.path.dirname(os.path.realpath(__file__)), cmd)]
    command.extend(sys.argv[1:])
    sys.exit(subprocess.call(command))


def qt_tool_wrapper(qt_tool, args, libexec=False):
    # Taking care of pyside6-uic, pyside6-rcc, and pyside6-designer
    # listed as an entrypoint in setup.py
    pyside_dir = Path(ref_mod.__file__).resolve().parent
    if libexec and sys.platform != "win32":
        exe = pyside_dir / 'Qt' / 'libexec' / qt_tool
    else:
        exe = pyside_dir / qt_tool

    cmd = [os.fspath(exe)] + args
    returncode = subprocess.call(cmd)
    if returncode != 0:
        command = ' '.join(cmd)
        print(f"'{command}' returned {returncode}", file=sys.stderr)
    sys.exit(returncode)


def pyside_script_wrapper(script_name):
    """Launch a script shipped with PySide."""
    script = Path(__file__).resolve().parent / script_name
    command = [sys.executable, os.fspath(script)] + sys.argv[1:]
    sys.exit(subprocess.call(command))


def ui_tool_binary(binary):
    """Return the binary of a UI tool (App bundle on macOS)."""
    if sys.platform != "darwin":
        return binary
    name = binary[0:1].upper() + binary[1:]
    return f"{name}.app/Contents/MacOS/{name}"


def lrelease():
    qt_tool_wrapper("lrelease", sys.argv[1:])


def lupdate():
    qt_tool_wrapper("lupdate", sys.argv[1:])


def uic():
    qt_tool_wrapper("uic", ['-g', 'python'] + sys.argv[1:], True)


def rcc():
    args = []
    user_args = sys.argv[1:]
    if "--binary" not in user_args:
        args.extend(['-g', 'python'])
    args.extend(user_args)
    qt_tool_wrapper("rcc", args, True)


def qmltyperegistrar():
    qt_tool_wrapper("qmltyperegistrar", sys.argv[1:], True)


def qmlimportscanner():
    qt_tool_wrapper("qmlimportscanner", sys.argv[1:], True)


def qmlcachegen():
    qt_tool_wrapper("qmlcachegen", sys.argv[1:], True)


def qmllint():
    qt_tool_wrapper("qmllint", sys.argv[1:])


def qmlformat():
    qt_tool_wrapper("qmlformat", sys.argv[1:])


def qmlls():
    qt_tool_wrapper("qmlls", sys.argv[1:])


def assistant():
    qt_tool_wrapper(ui_tool_binary("assistant"), sys.argv[1:])


def _extend_path_var(var, value, prepend=False):
    env_value = os.environ.get(var)
    if env_value:
        env_value = (f'{value}{os.pathsep}{env_value}'
                     if prepend else f'{env_value}{os.pathsep}{value}')
    else:
        env_value = value
    os.environ[var] = env_value


def designer():
    init_virtual_env()

    # https://www.python.org/dev/peps/pep-0384/#linkage :
    # "On Unix systems, the ABI is typically provided by the python executable
    # itself", that is, libshiboken does not link against any Python library
    # and expects to get these symbols from a python executable. Since no
    # python executable is involved when loading this plugin, pre-load python.so
    # This should also help to work around a numpy issue, see
    # https://stackoverflow.com/questions/49784583/numpy-import-fails-on-multiarray-extension-library-when-called-from-embedded-pyt
    major_version = sys.version_info[0]
    minor_version = sys.version_info[1]
    os.environ['PY_MAJOR_VERSION'] = str(major_version)
    os.environ['PY_MINOR_VERSION'] = str(minor_version)
    if sys.platform == 'linux':
        # Determine library name (examples/utils/pyside_config.py)
        version = f'{major_version}.{minor_version}'
        library_name = f'libpython{version}{sys.abiflags}.so'
        if is_pyenv_python():
            library_name = str(Path(sysconfig.get_config_var('LIBDIR')) / library_name)
        os.environ['LD_PRELOAD'] = library_name
    elif sys.platform == 'darwin':
        library_name = sysconfig.get_config_var("LDLIBRARY")
        framework_prefix = sysconfig.get_config_var("PYTHONFRAMEWORKPREFIX")
        lib_path = None
        if framework_prefix:
            lib_path = os.fspath(Path(framework_prefix) / library_name)
        elif is_pyenv_python():
            lib_path = str(Path(sysconfig.get_config_var('LIBDIR')) / library_name)
        else:
            # ideally this should never be reached because the system Python and Python installed
            # from python.org are all framework builds
            print("Unable to find Python library directory. Use a framework build of Python.",
                  file=sys.stderr)
            sys.exit(0)
        os.environ['DYLD_INSERT_LIBRARIES'] = lib_path
    elif sys.platform == 'win32':
        # Find Python DLLs from the base installation
        if is_virtual_env():
            _extend_path_var("PATH", os.fspath(Path(sys._base_executable).parent), True)

    qt_tool_wrapper(ui_tool_binary("designer"), sys.argv[1:])


def linguist():
    qt_tool_wrapper(ui_tool_binary("linguist"), sys.argv[1:])


def genpyi():
    pyside_dir = Path(__file__).resolve().parents[1]
    support = pyside_dir / "support"
    cmd = support / "generate_pyi.py"
    command = [sys.executable, os.fspath(cmd)] + sys.argv[1:]
    sys.exit(subprocess.call(command))


def metaobjectdump():
    pyside_script_wrapper("metaobjectdump.py")


def _check_requirements(requirements_file):
    """Check if all required packages are installed."""
    missing_packages = []
    with open(requirements_file, 'r', encoding='UTF-8') as file:
        for line in file:
            # versions
            package = line.strip().split('==')[0]
            if not importlib.util.find_spec(package):
                missing_packages.append(line.strip())
    return missing_packages


def project():
    pyside_script_wrapper("project.py")


def qml():
    pyside_script_wrapper("qml.py")


def qtpy2cpp():
    pyside_script_wrapper("qtpy2cpp.py")


def deploy():
    pyside_script_wrapper("deploy.py")


def android_deploy():
    if sys.platform == "win32":
        print("pyside6-android-deploy only works from a Unix host and not a Windows host",
              file=sys.stderr)
    else:
        android_requirements_file = Path(__file__).parent / "requirements-android.txt"
        if android_requirements_file.exists():
            missing_packages = _check_requirements(android_requirements_file)
            if missing_packages:
                print("The following packages are required but not installed:")
                for package in missing_packages:
                    print(f"  - {package}")
                print("Please install them using:")
                print(f"  pip install -r {android_requirements_file}")
                sys.exit(1)
        pyside_script_wrapper("android_deploy.py")


def qsb():
    qt_tool_wrapper("qsb", sys.argv[1:])


def balsam():
    qt_tool_wrapper("balsam", sys.argv[1:])


def balsamui():
    qt_tool_wrapper("balsamui", sys.argv[1:])


def svgtoqml():
    qt_tool_wrapper("svgtoqml", sys.argv[1:])


if __name__ == "__main__":
    main()
