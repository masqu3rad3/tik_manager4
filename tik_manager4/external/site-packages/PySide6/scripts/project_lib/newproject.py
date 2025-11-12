# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .pyproject_toml import write_pyproject_toml
from .pyproject_json import write_pyproject_json

"""New project generation code."""

_WIDGET_MAIN = """if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
"""

_WIDGET_IMPORTS = """import sys
from PySide6.QtWidgets import QApplication, QMainWindow
"""

_WIDGET_CLASS_DEFINITION = """class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
"""

_WIDGET_SETUP_UI_CODE = """        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
"""

_MAINWINDOW_FORM = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget"/>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>22</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
</ui>
"""

_QUICK_FORM = """import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
}
"""

_QUICK_MAIN = """import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine


if __name__ == "__main__":
    app = QGuiApplication()
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).parent / 'main.qml'
    engine.load(QUrl.fromLocalFile(qml_file))
    if not engine.rootObjects():
        sys.exit(-1)
    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
"""

NewProjectFiles = list[tuple[str, str]]  # tuple of (filename, contents).


@dataclass(frozen=True)
class NewProjectType:
    command: str
    description: str
    files: NewProjectFiles


def _write_project(directory: Path, files: NewProjectFiles, legacy_pyproject: bool):
    """
    Create the project files in the specified directory.

    :param directory: The directory to create the project in.
    :param files: The files that belong to the project to create.
    """
    file_names = []
    for file_name, contents in files:
        (directory / file_name).write_text(contents)
        print(f"Wrote {directory.name}{os.sep}{file_name}.")
        file_names.append(file_name)

    if legacy_pyproject:
        pyproject_file = directory / f"{directory.name}.pyproject"
        write_pyproject_json(pyproject_file, file_names)
    else:
        pyproject_file = directory / "pyproject.toml"
        write_pyproject_toml(pyproject_file, directory.name, file_names)
    print(f"Wrote {pyproject_file}.")


def _widget_project() -> NewProjectFiles:
    """Create a (form-less) widgets project."""
    main_py = (_WIDGET_IMPORTS + "\n\n" + _WIDGET_CLASS_DEFINITION + "\n\n"
               + _WIDGET_MAIN)
    return [("main.py", main_py)]


def _ui_form_project() -> NewProjectFiles:
    """Create a Qt Designer .ui form based widgets project."""
    main_py = (_WIDGET_IMPORTS
               + "\nfrom ui_mainwindow import Ui_MainWindow\n\n\n"
               + _WIDGET_CLASS_DEFINITION + _WIDGET_SETUP_UI_CODE
               + "\n\n" + _WIDGET_MAIN)
    return [("main.py", main_py),
            ("mainwindow.ui", _MAINWINDOW_FORM)]


def _qml_project() -> NewProjectFiles:
    """Create a QML project."""
    return [("main.py", _QUICK_MAIN),
            ("main.qml", _QUICK_FORM)]


class NewProjectTypes(Enum):
    QUICK = NewProjectType("new-quick", "Create a new Qt Quick project", _qml_project())
    WIDGET_FORM = NewProjectType("new-ui", "Create a new Qt Widgets Form project",
                                 _ui_form_project())
    WIDGET = NewProjectType("new-widget", "Create a new Qt Widgets project", _widget_project())

    @staticmethod
    def find_by_command(command: str) -> NewProjectType | None:
        return next((pt.value for pt in NewProjectTypes if pt.value.command == command), None)


def new_project(
    project_dir: Path, project_type: NewProjectType, legacy_pyproject: bool
) -> int:
    """
    Create a new project at the specified project_dir directory.

    :param project_dir: The directory path to create the project. If existing, must be empty.
    :param project_type: The Qt type of project to create (Qt Widgets, Qt Quick, etc.)

    :return: 0 if the project was created successfully, otherwise 1.
    """
    if any(project_dir.iterdir()):
        print(f"Can not create project at {project_dir}: directory is not empty.", file=sys.stderr)
        return 1
    project_dir.mkdir(parents=True, exist_ok=True)

    try:
        _write_project(project_dir, project_type.files, legacy_pyproject)
    except Exception as e:
        print(f"Error creating project file: {str(e)}", file=sys.stderr)
        return 1

    if project_type == NewProjectTypes.WIDGET_FORM:
        print(f'Run "pyside6-project build {project_dir}" to build the project')
    print(f'Run "pyside6-project run {project_dir / "main.py"}" to run the project')
    return 0
