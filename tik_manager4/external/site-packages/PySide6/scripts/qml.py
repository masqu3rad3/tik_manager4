# Copyright (C) 2018 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""pyside6-qml tool implementation. This tool mimics the capabilities of qml runtime utility
for python and enables quick protyping with python modules"""

import argparse
import importlib.util
import logging
import sys
import os
from pathlib import Path
from pprint import pprint

from PySide6.QtCore import QCoreApplication, Qt, QLibraryInfo, QUrl, SignalInstance
from PySide6.QtGui import QGuiApplication, QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuick import QQuickView, QQuickItem
from PySide6.QtWidgets import QApplication


def import_qml_modules(qml_parent_path: Path, module_paths: list[Path] = []):
    '''
    Import all the python modules in the qml_parent_path. This way all the classes
    containing the @QmlElement/@QmlNamedElement are also imported

        Parameters:
                qml_parent_path (Path): Parent directory of the qml file
                module_paths (int): user give import paths obtained through cli
    '''

    search_dir_paths = []
    search_file_paths = []

    if not module_paths:
        search_dir_paths.append(qml_parent_path)
    else:
        for module_path in module_paths:
            if module_path.is_dir():
                search_dir_paths.append(module_path)
            elif module_path.exists() and module_path.suffix == ".py":
                search_file_paths.append(module_path)

    def import_module(import_module_paths: set[Path]):
        """Import the modules in 'import_module_paths'"""
        for module_path in import_module_paths:
            module_name = module_path.name[:-3]
            _spec = importlib.util.spec_from_file_location(f"{module_name}", module_path)
            _module = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(module=_module)

    modules_to_import = set()
    for search_path in search_dir_paths:
        possible_modules = list(search_path.glob("**/*.py"))
        for possible_module in possible_modules:
            if possible_module.is_file() and possible_module.name != "__init__.py":
                module_parent = str(possible_module.parent)
                if module_parent not in sys.path:
                    sys.path.append(module_parent)
                modules_to_import.add(possible_module)

    for search_path in search_file_paths:
        sys.path.append(str(search_path.parent))
        modules_to_import.add(search_path)

    import_module(import_module_paths=modules_to_import)


def print_configurations():
    return "Built-in configurations \n\t default \n\t resizeToItem"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This tools mimics the capabilities of qml runtime utility by directly"
        " invoking QQmlEngine/QQuickView. It enables quick prototyping with qml files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "file",
        type=lambda p: Path(p).absolute(),
        help="Path to qml file to display",
    )
    parser.add_argument(
        "--module-paths", "-I",
        type=lambda p: Path(p).absolute(),
        nargs="+",
        help="Specify space separated folder/file paths where the Qml classes are defined. By"
             " default,the parent directory of the qml_path is searched recursively for all .py"
             " files and they are imported. Otherwise only the paths give in module paths are"
             " searched",
    )
    parser.add_argument(
        "--list-conf",
        action="version",
        help="List the built-in configurations.",
        version=print_configurations()
    )
    parser.add_argument(
        "--apptype", "-a",
        choices=["core", "gui", "widget"],
        default="gui",
        help="Select which application class to use. Default is gui",
    )
    parser.add_argument(
        "--config", "-c",
        choices=["default", "resizeToItem"],
        default="default",
        help="Select the built-in configurations.",
    )
    parser.add_argument(
        "--rhi", "-r",
        choices=["vulkan", "metal", "d3dll", "gl"],
        help="Set the backend for the Qt graphics abstraction (RHI).",
    )
    parser.add_argument(
        "--core-profile",
        action="store_true",
        help="Force use of OpenGL Core Profile.",
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Print information about what qml is doing, like specific file URLs being loaded.",
        action="store_const", dest="loglevel", const=logging.INFO,
    )

    gl_group = parser.add_mutually_exclusive_group(required=False)
    gl_group.add_argument(
        "--gles",
        action="store_true",
        help="Force use of GLES (AA_UseOpenGLES)",
    )
    gl_group.add_argument(
        "--desktop",
        action="store_true",
        help="Force use of desktop OpenGL (AA_UseDesktopOpenGL)",
    )
    gl_group.add_argument(
        "--software",
        action="store_true",
        help="Force use of software rendering(AA_UseSoftwareOpenGL)",
    )
    gl_group.add_argument(
        "--disable-context-sharing",
        action="store_true",
        help=" Disable the use of a shared GL context for QtQuick Windows",
    )

    args = parser.parse_args()
    apptype = args.apptype

    qquick_present = False

    with open(args.file) as myfile:
        if 'import QtQuick' in myfile.read():
            qquick_present = True

    # no import QtQuick => QQCoreApplication
    if not qquick_present:
        apptype = "core"

    import_qml_modules(args.file.parent, args.module_paths)

    logging.basicConfig(level=args.loglevel)
    logging.info(f"qml: {QLibraryInfo.build()}")
    logging.info(f"qml: Using built-in configuration: {args.config}")

    if args.rhi:
        os.environ['QSG_RHI_BACKEND'] = args.rhi

    logging.info(f"qml: loading {args.file}")
    qml_file = QUrl.fromLocalFile(str(args.file))

    if apptype == "gui":
        if args.gles:
            logging.info("qml: Using attribute AA_UseOpenGLES")
            QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)
        elif args.desktop:
            logging.info("qml: Using attribute AA_UseDesktopOpenGL")
            QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
        elif args.software:
            logging.info("qml: Using attribute AA_UseSoftwareOpenGL")
            QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

        # context-sharing is enabled by default
        if not args.disable_context_sharing:
            logging.info("qml: Using attribute AA_ShareOpenGLContexts")
            QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    if apptype == "core":
        logging.info("qml: Core application")
        app = QCoreApplication(sys.argv)
    elif apptype == "widgets":
        logging.info("qml: Widget application")
        app = QApplication(sys.argv)
    else:
        logging.info("qml: Gui application")
        app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    # set OpenGLContextProfile
    if apptype == "gui" and args.core_profile:
        logging.info("qml: Set profile for QSurfaceFormat as CoreProfile")
        surfaceFormat = QSurfaceFormat()
        surfaceFormat.setStencilBufferSize(8)
        surfaceFormat.setDepthBufferSize(24)
        surfaceFormat.setVersion(4, 1)
        surfaceFormat.setProfile(QSurfaceFormat.CoreProfile)
        QSurfaceFormat.setDefaultFormat(surfaceFormat)

    # in the case of QCoreApplication we print the attributes of the object created via
    # QQmlComponent and exit
    if apptype == "core":
        component = QQmlComponent(engine, qml_file)
        obj = component.create()
        filtered_attributes = {k: v for k, v in vars(obj).items() if type(v) is not SignalInstance}
        logging.info("qml: component object attributes are")
        pprint(filtered_attributes)
        del engine
        sys.exit(0)

    engine.load(qml_file)
    rootObjects = engine.rootObjects()
    if not rootObjects:
        sys.exit(-1)

    qquick_view = False
    if isinstance(rootObjects[0], QQuickItem) and qquick_present:
        logging.info("qml: loading with QQuickView")
        viewer = QQuickView()
        viewer.setSource(qml_file)
        if args.config != "resizeToItem":
            viewer.setResizeMode(QQuickView.SizeRootObjectToView)
        else:
            viewer.setResizeMode(QQuickView.SizeViewToRootObject)
        viewer.show()
        qquick_view = True

    if not qquick_view:
        logging.info("qml: loading with QQmlApplicationEngine")
        if args.config == "resizeToItem":
            logging.info("qml: Not a QQuickview item. resizeToItem is done by default")

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
