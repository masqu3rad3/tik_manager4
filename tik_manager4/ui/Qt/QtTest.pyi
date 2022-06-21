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
PySide2.QtTest, except for defaults which are replaced by "...".
"""

# Module PySide2.QtTest
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
import PySide2.QtGui
import PySide2.QtWidgets
import PySide2.QtTest


class QTest(Shiboken.Object):
    FramesPerSecond          : QTest = ... # 0x0
    MousePress               : QTest = ... # 0x0
    Press                    : QTest = ... # 0x0
    Abort                    : QTest = ... # 0x1
    BitsPerSecond            : QTest = ... # 0x1
    MouseRelease             : QTest = ... # 0x1
    Release                  : QTest = ... # 0x1
    BytesPerSecond           : QTest = ... # 0x2
    Click                    : QTest = ... # 0x2
    Continue                 : QTest = ... # 0x2
    MouseClick               : QTest = ... # 0x2
    MouseDClick              : QTest = ... # 0x3
    Shortcut                 : QTest = ... # 0x3
    WalltimeMilliseconds     : QTest = ... # 0x3
    CPUTicks                 : QTest = ... # 0x4
    MouseMove                : QTest = ... # 0x4
    InstructionReads         : QTest = ... # 0x5
    Events                   : QTest = ... # 0x6
    WalltimeNanoseconds      : QTest = ... # 0x7
    BytesAllocated           : QTest = ... # 0x8
    CPUMigrations            : QTest = ... # 0x9
    CPUCycles                : QTest = ... # 0xa
    BusCycles                : QTest = ... # 0xb
    StalledCycles            : QTest = ... # 0xc
    Instructions             : QTest = ... # 0xd
    BranchInstructions       : QTest = ... # 0xe
    BranchMisses             : QTest = ... # 0xf
    CacheReferences          : QTest = ... # 0x10
    CacheReads               : QTest = ... # 0x11
    CacheWrites              : QTest = ... # 0x12
    CachePrefetches          : QTest = ... # 0x13
    CacheMisses              : QTest = ... # 0x14
    CacheReadMisses          : QTest = ... # 0x15
    CacheWriteMisses         : QTest = ... # 0x16
    CachePrefetchMisses      : QTest = ... # 0x17
    ContextSwitches          : QTest = ... # 0x18
    PageFaults               : QTest = ... # 0x19
    MinorPageFaults          : QTest = ... # 0x1a
    MajorPageFaults          : QTest = ... # 0x1b
    AlignmentFaults          : QTest = ... # 0x1c
    EmulationFaults          : QTest = ... # 0x1d
    RefCPUCycles             : QTest = ... # 0x1e

    class KeyAction(object):
        Press                    : QTest.KeyAction = ... # 0x0
        Release                  : QTest.KeyAction = ... # 0x1
        Click                    : QTest.KeyAction = ... # 0x2
        Shortcut                 : QTest.KeyAction = ... # 0x3

    class MouseAction(object):
        MousePress               : QTest.MouseAction = ... # 0x0
        MouseRelease             : QTest.MouseAction = ... # 0x1
        MouseClick               : QTest.MouseAction = ... # 0x2
        MouseDClick              : QTest.MouseAction = ... # 0x3
        MouseMove                : QTest.MouseAction = ... # 0x4

    class QBenchmarkMetric(object):
        FramesPerSecond          : QTest.QBenchmarkMetric = ... # 0x0
        BitsPerSecond            : QTest.QBenchmarkMetric = ... # 0x1
        BytesPerSecond           : QTest.QBenchmarkMetric = ... # 0x2
        WalltimeMilliseconds     : QTest.QBenchmarkMetric = ... # 0x3
        CPUTicks                 : QTest.QBenchmarkMetric = ... # 0x4
        InstructionReads         : QTest.QBenchmarkMetric = ... # 0x5
        Events                   : QTest.QBenchmarkMetric = ... # 0x6
        WalltimeNanoseconds      : QTest.QBenchmarkMetric = ... # 0x7
        BytesAllocated           : QTest.QBenchmarkMetric = ... # 0x8
        CPUMigrations            : QTest.QBenchmarkMetric = ... # 0x9
        CPUCycles                : QTest.QBenchmarkMetric = ... # 0xa
        BusCycles                : QTest.QBenchmarkMetric = ... # 0xb
        StalledCycles            : QTest.QBenchmarkMetric = ... # 0xc
        Instructions             : QTest.QBenchmarkMetric = ... # 0xd
        BranchInstructions       : QTest.QBenchmarkMetric = ... # 0xe
        BranchMisses             : QTest.QBenchmarkMetric = ... # 0xf
        CacheReferences          : QTest.QBenchmarkMetric = ... # 0x10
        CacheReads               : QTest.QBenchmarkMetric = ... # 0x11
        CacheWrites              : QTest.QBenchmarkMetric = ... # 0x12
        CachePrefetches          : QTest.QBenchmarkMetric = ... # 0x13
        CacheMisses              : QTest.QBenchmarkMetric = ... # 0x14
        CacheReadMisses          : QTest.QBenchmarkMetric = ... # 0x15
        CacheWriteMisses         : QTest.QBenchmarkMetric = ... # 0x16
        CachePrefetchMisses      : QTest.QBenchmarkMetric = ... # 0x17
        ContextSwitches          : QTest.QBenchmarkMetric = ... # 0x18
        PageFaults               : QTest.QBenchmarkMetric = ... # 0x19
        MinorPageFaults          : QTest.QBenchmarkMetric = ... # 0x1a
        MajorPageFaults          : QTest.QBenchmarkMetric = ... # 0x1b
        AlignmentFaults          : QTest.QBenchmarkMetric = ... # 0x1c
        EmulationFaults          : QTest.QBenchmarkMetric = ... # 0x1d
        RefCPUCycles             : QTest.QBenchmarkMetric = ... # 0x1e

    class QTouchEventSequence(Shiboken.Object):
        def commit(self, processEvents:bool=...): ...
        @typing.overload
        def move(self, touchId:int, pt:PySide2.QtCore.QPoint, widget:typing.Optional[PySide2.QtWidgets.QWidget]=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def move(self, touchId:int, pt:PySide2.QtCore.QPoint, window:typing.Optional[PySide2.QtGui.QWindow]=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def press(self, touchId:int, pt:PySide2.QtCore.QPoint, widget:typing.Optional[PySide2.QtWidgets.QWidget]=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def press(self, touchId:int, pt:PySide2.QtCore.QPoint, window:typing.Optional[PySide2.QtGui.QWindow]=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def release(self, touchId:int, pt:PySide2.QtCore.QPoint, widget:typing.Optional[PySide2.QtWidgets.QWidget]=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def release(self, touchId:int, pt:PySide2.QtCore.QPoint, window:typing.Optional[PySide2.QtGui.QWindow]=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...
        def stationary(self, touchId:int) -> PySide2.QtTest.QTest.QTouchEventSequence: ...

    class TestFailMode(object):
        Abort                    : QTest.TestFailMode = ... # 0x1
        Continue                 : QTest.TestFailMode = ... # 0x2
    @staticmethod
    def addColumnInternal(id:int, name:bytes): ...
    @staticmethod
    def asciiToKey(ascii:int) -> PySide2.QtCore.Qt.Key: ...
    @staticmethod
    def compare_ptr_helper(t1:int, t2:int, actual:bytes, expected:bytes, file:bytes, line:int) -> bool: ...
    @staticmethod
    def compare_string_helper(t1:bytes, t2:bytes, actual:bytes, expected:bytes, file:bytes, line:int) -> bool: ...
    @staticmethod
    def createTouchDevice(devType:PySide2.QtGui.QTouchDevice.DeviceType=...) -> PySide2.QtGui.QTouchDevice: ...
    @staticmethod
    def currentAppName() -> bytes: ...
    @staticmethod
    def currentDataTag() -> bytes: ...
    @staticmethod
    def currentTestFailed() -> bool: ...
    @staticmethod
    def currentTestFunction() -> bytes: ...
    @typing.overload
    @staticmethod
    def ignoreMessage(type:PySide2.QtCore.QtMsgType, message:bytes): ...
    @typing.overload
    @staticmethod
    def ignoreMessage(type:PySide2.QtCore.QtMsgType, messagePattern:PySide2.QtCore.QRegularExpression): ...
    @typing.overload
    @staticmethod
    def keyClick(widget:PySide2.QtWidgets.QWidget, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyClick(widget:PySide2.QtWidgets.QWidget, key:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyClick(window:PySide2.QtGui.QWindow, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyClick(window:PySide2.QtGui.QWindow, key:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @staticmethod
    def keyClicks(widget:PySide2.QtWidgets.QWidget, sequence:str, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyEvent(action:PySide2.QtTest.QTest.KeyAction, widget:PySide2.QtWidgets.QWidget, ascii:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyEvent(action:PySide2.QtTest.QTest.KeyAction, widget:PySide2.QtWidgets.QWidget, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyEvent(action:PySide2.QtTest.QTest.KeyAction, window:PySide2.QtGui.QWindow, ascii:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyEvent(action:PySide2.QtTest.QTest.KeyAction, window:PySide2.QtGui.QWindow, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyPress(widget:PySide2.QtWidgets.QWidget, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyPress(widget:PySide2.QtWidgets.QWidget, key:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyPress(window:PySide2.QtGui.QWindow, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyPress(window:PySide2.QtGui.QWindow, key:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyRelease(widget:PySide2.QtWidgets.QWidget, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyRelease(widget:PySide2.QtWidgets.QWidget, key:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyRelease(window:PySide2.QtGui.QWindow, key:PySide2.QtCore.Qt.Key, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keyRelease(window:PySide2.QtGui.QWindow, key:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def keySequence(widget:PySide2.QtWidgets.QWidget, keySequence:PySide2.QtGui.QKeySequence): ...
    @typing.overload
    @staticmethod
    def keySequence(window:PySide2.QtGui.QWindow, keySequence:PySide2.QtGui.QKeySequence): ...
    @staticmethod
    def keyToAscii(key:PySide2.QtCore.Qt.Key) -> int: ...
    @typing.overload
    @staticmethod
    def mouseClick(widget:PySide2.QtWidgets.QWidget, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseClick(window:PySide2.QtGui.QWindow, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseDClick(widget:PySide2.QtWidgets.QWidget, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseDClick(window:PySide2.QtGui.QWindow, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseEvent(action:PySide2.QtTest.QTest.MouseAction, widget:PySide2.QtWidgets.QWidget, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers, pos:PySide2.QtCore.QPoint, delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseEvent(action:PySide2.QtTest.QTest.MouseAction, window:PySide2.QtGui.QWindow, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers, pos:PySide2.QtCore.QPoint, delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseMove(widget:PySide2.QtWidgets.QWidget, pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseMove(window:PySide2.QtGui.QWindow, pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mousePress(widget:PySide2.QtWidgets.QWidget, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mousePress(window:PySide2.QtGui.QWindow, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseRelease(widget:PySide2.QtWidgets.QWidget, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @typing.overload
    @staticmethod
    def mouseRelease(window:PySide2.QtGui.QWindow, button:PySide2.QtCore.Qt.MouseButton, stateKey:PySide2.QtCore.Qt.KeyboardModifiers=..., pos:PySide2.QtCore.QPoint=..., delay:int=...): ...
    @staticmethod
    def qCleanup(): ...
    @staticmethod
    def qElementData(elementName:bytes, metaTypeId:int) -> int: ...
    @staticmethod
    def qExpectFail(dataIndex:bytes, comment:bytes, mode:PySide2.QtTest.QTest.TestFailMode, file:bytes, line:int) -> bool: ...
    @typing.overload
    @staticmethod
    def qFindTestData(basepath:str, file:typing.Optional[bytes]=..., line:int=..., builddir:typing.Optional[bytes]=...) -> str: ...
    @typing.overload
    @staticmethod
    def qFindTestData(basepath:bytes, file:typing.Optional[bytes]=..., line:int=..., builddir:typing.Optional[bytes]=...) -> str: ...
    @staticmethod
    def qGlobalData(tagName:bytes, typeId:int) -> int: ...
    @staticmethod
    def qRun() -> int: ...
    @staticmethod
    def qSkip(message:bytes, file:bytes, line:int): ...
    @staticmethod
    def qWaitForWindowActive(widget:PySide2.QtWidgets.QWidget, timeout:int=...) -> bool: ...
    @staticmethod
    def qWaitForWindowExposed(widget:PySide2.QtWidgets.QWidget, timeout:int=...) -> bool: ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action:PySide2.QtTest.QTest.KeyAction, widget:PySide2.QtWidgets.QWidget, code:PySide2.QtCore.Qt.Key, ascii:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers, delay:int=...): ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action:PySide2.QtTest.QTest.KeyAction, widget:PySide2.QtWidgets.QWidget, code:PySide2.QtCore.Qt.Key, text:str, modifier:PySide2.QtCore.Qt.KeyboardModifiers, delay:int=...): ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action:PySide2.QtTest.QTest.KeyAction, window:PySide2.QtGui.QWindow, code:PySide2.QtCore.Qt.Key, ascii:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers, delay:int=...): ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action:PySide2.QtTest.QTest.KeyAction, window:PySide2.QtGui.QWindow, code:PySide2.QtCore.Qt.Key, text:str, modifier:PySide2.QtCore.Qt.KeyboardModifiers, delay:int=...): ...
    @staticmethod
    def setBenchmarkResult(result:float, metric:PySide2.QtTest.QTest.QBenchmarkMetric): ...
    @staticmethod
    def setMainSourcePath(file:bytes, builddir:typing.Optional[bytes]=...): ...
    @typing.overload
    @staticmethod
    def simulateEvent(widget:PySide2.QtWidgets.QWidget, press:bool, code:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers, text:str, repeat:bool, delay:int=...): ...
    @typing.overload
    @staticmethod
    def simulateEvent(window:PySide2.QtGui.QWindow, press:bool, code:int, modifier:PySide2.QtCore.Qt.KeyboardModifiers, text:str, repeat:bool, delay:int=...): ...
    @staticmethod
    def testObject() -> PySide2.QtCore.QObject: ...
    @staticmethod
    def toPrettyCString(unicode:bytes, length:int) -> bytes: ...
    @typing.overload
    @staticmethod
    def touchEvent(widget:PySide2.QtWidgets.QWidget, device:PySide2.QtGui.QTouchDevice, autoCommit:bool=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...
    @typing.overload
    @staticmethod
    def touchEvent(window:PySide2.QtGui.QWindow, device:PySide2.QtGui.QTouchDevice, autoCommit:bool=...) -> PySide2.QtTest.QTest.QTouchEventSequence: ...

# eof
