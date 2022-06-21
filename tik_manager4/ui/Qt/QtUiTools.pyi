# This Python file uses the following encoding: utf-8
#############################################################################
##
## Copyright (C) 2020 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

"""
This file contains the exact signatures for all functions in module
PySide2.QtUiTools, except for defaults which are replaced by "...".
"""

# Module PySide2.QtUiTools
import PySide2
try:
    import typing
except ImportError:
    from PySide2.support.signature import typing
from PySide2.support.signature.mapping import (
    Virtual, Missing, Invalid, Default, Instance)

class Object(object): pass

import shiboken2 as Shiboken
Shiboken.Object = Object

import PySide2.QtCore
import PySide2.QtWidgets
import PySide2.QtUiTools


class QUiLoader(PySide2.QtCore.QObject):

    def __init__(self, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...

    def addPluginPath(self, path:str): ...
    def availableLayouts(self) -> typing.List: ...
    def availableWidgets(self) -> typing.List: ...
    def clearPluginPaths(self): ...
    def createAction(self, parent:typing.Optional[PySide2.QtCore.QObject]=..., name:str=...) -> PySide2.QtWidgets.QAction: ...
    def createActionGroup(self, parent:typing.Optional[PySide2.QtCore.QObject]=..., name:str=...) -> PySide2.QtWidgets.QActionGroup: ...
    def createLayout(self, className:str, parent:typing.Optional[PySide2.QtCore.QObject]=..., name:str=...) -> PySide2.QtWidgets.QLayout: ...
    def createWidget(self, className:str, parent:typing.Optional[PySide2.QtWidgets.QWidget]=..., name:str=...) -> PySide2.QtWidgets.QWidget: ...
    def errorString(self) -> str: ...
    def isLanguageChangeEnabled(self) -> bool: ...
    def isTranslationEnabled(self) -> bool: ...
    @typing.overload
    def load(self, arg__1:str, parentWidget:typing.Optional[PySide2.QtWidgets.QWidget]=...) -> PySide2.QtWidgets.QWidget: ...
    @typing.overload
    def load(self, device:PySide2.QtCore.QIODevice, parentWidget:typing.Optional[PySide2.QtWidgets.QWidget]=...) -> PySide2.QtWidgets.QWidget: ...
    def pluginPaths(self) -> typing.List: ...
    def registerCustomWidget(self, customWidgetType:object): ...
    def setLanguageChangeEnabled(self, enabled:bool): ...
    def setTranslationEnabled(self, enabled:bool): ...
    def setWorkingDirectory(self, dir:PySide2.QtCore.QDir): ...
    def workingDirectory(self) -> PySide2.QtCore.QDir: ...
def loadUiType(uifile:str) -> object: ...

# eof
