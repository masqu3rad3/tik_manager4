# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
"""
This file contains the exact signatures for all functions in module
PySide6.QtTest, except for defaults which are replaced by "...".

# mypy: disable-error-code="override, overload-overlap"
"""

# Module `PySide6.QtTest`

import PySide6.QtTest
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets

import enum
import typing
from PySide6.QtCore import SignalInstance
from shiboken6 import Shiboken


class QAbstractItemModelTester(PySide6.QtCore.QObject):

    class FailureReportingMode(enum.Enum):

        QtTest                    = ...  # 0x0
        Warning                   = ...  # 0x1
        Fatal                     = ...  # 0x2


    @typing.overload
    def __init__(self, model: PySide6.QtCore.QAbstractItemModel, mode: PySide6.QtTest.QAbstractItemModelTester.FailureReportingMode, /, parent: PySide6.QtCore.QObject | None = ...) -> None: ...
    @typing.overload
    def __init__(self, model: PySide6.QtCore.QAbstractItemModel, /, parent: PySide6.QtCore.QObject | None = ...) -> None: ...

    def failureReportingMode(self, /) -> PySide6.QtTest.QAbstractItemModelTester.FailureReportingMode: ...
    def model(self, /) -> PySide6.QtCore.QAbstractItemModel: ...
    def setUseFetchMore(self, value: bool, /) -> None: ...


class QIntList: ...


class QSignalSpy(Shiboken.Object):

    @typing.overload
    def __init__(self, obj: PySide6.QtCore.QObject, signal: PySide6.QtCore.QMetaMethod, /) -> None: ...
    @typing.overload
    def __init__(self, obj: PySide6.QtCore.QObject, aSignal: bytes | bytearray | memoryview, /) -> None: ...
    @typing.overload
    def __init__(self, signal: PySide6.QtCore.SignalInstance, /) -> None: ...

    def at(self, arg__1: int, /) -> typing.List[typing.Any]: ...
    def count(self, /) -> int: ...
    def isValid(self, /) -> bool: ...
    def signal(self, /) -> PySide6.QtCore.QByteArray: ...
    def size(self, /) -> int: ...
    def wait(self, timeout: int, /) -> bool: ...


class QTest(Shiboken.Object):

    class ComparisonOperation(enum.Enum):

        CustomCompare             = ...  # 0x0
        Equal                     = ...  # 0x1
        NotEqual                  = ...  # 0x2
        LessThan                  = ...  # 0x3
        LessThanOrEqual           = ...  # 0x4
        GreaterThan               = ...  # 0x5
        GreaterThanOrEqual        = ...  # 0x6
        ThreeWayCompare           = ...  # 0x7

    class KeyAction(enum.Enum):

        Press                     = ...  # 0x0
        Release                   = ...  # 0x1
        Click                     = ...  # 0x2
        Shortcut                  = ...  # 0x3

    class MouseAction(enum.Enum):

        MousePress                = ...  # 0x0
        MouseRelease              = ...  # 0x1
        MouseClick                = ...  # 0x2
        MouseDClick               = ...  # 0x3
        MouseMove                 = ...  # 0x4

    class QBenchmarkMetric(enum.Enum):

        FramesPerSecond           = ...  # 0x0
        BitsPerSecond             = ...  # 0x1
        BytesPerSecond            = ...  # 0x2
        WalltimeMilliseconds      = ...  # 0x3
        CPUTicks                  = ...  # 0x4
        InstructionReads          = ...  # 0x5
        Events                    = ...  # 0x6
        WalltimeNanoseconds       = ...  # 0x7
        BytesAllocated            = ...  # 0x8
        CPUMigrations             = ...  # 0x9
        CPUCycles                 = ...  # 0xa
        BusCycles                 = ...  # 0xb
        StalledCycles             = ...  # 0xc
        Instructions              = ...  # 0xd
        BranchInstructions        = ...  # 0xe
        BranchMisses              = ...  # 0xf
        CacheReferences           = ...  # 0x10
        CacheReads                = ...  # 0x11
        CacheWrites               = ...  # 0x12
        CachePrefetches           = ...  # 0x13
        CacheMisses               = ...  # 0x14
        CacheReadMisses           = ...  # 0x15
        CacheWriteMisses          = ...  # 0x16
        CachePrefetchMisses       = ...  # 0x17
        ContextSwitches           = ...  # 0x18
        PageFaults                = ...  # 0x19
        MinorPageFaults           = ...  # 0x1a
        MajorPageFaults           = ...  # 0x1b
        AlignmentFaults           = ...  # 0x1c
        EmulationFaults           = ...  # 0x1d
        RefCPUCycles              = ...  # 0x1e

    class QTouchEventSequence(Shiboken.Object):
        def commit(self, /, processEvents: bool = ...) -> None: ...
        @typing.overload
        def move(self, touchId: int, pt: PySide6.QtCore.QPoint, /, widget: PySide6.QtWidgets.QWidget | None = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def move(self, touchId: int, pt: PySide6.QtCore.QPoint, /, window: PySide6.QtGui.QWindow | None = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def press(self, touchId: int, pt: PySide6.QtCore.QPoint, /, widget: PySide6.QtWidgets.QWidget | None = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def press(self, touchId: int, pt: PySide6.QtCore.QPoint, /, window: PySide6.QtGui.QWindow | None = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def release(self, touchId: int, pt: PySide6.QtCore.QPoint, /, widget: PySide6.QtWidgets.QWidget | None = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
        @typing.overload
        def release(self, touchId: int, pt: PySide6.QtCore.QPoint, /, window: PySide6.QtGui.QWindow | None = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
        def stationary(self, touchId: int, /) -> PySide6.QtTest.QTest.QTouchEventSequence: ...

    class TestFailMode(enum.Enum):

        Abort                     = ...  # 0x1
        Continue                  = ...  # 0x2


    @staticmethod
    def addColumnInternal(id: int, name: bytes | bytearray | memoryview, /) -> None: ...
    @staticmethod
    def asciiToKey(ascii: int, /) -> PySide6.QtCore.Qt.Key: ...
    @typing.overload
    @staticmethod
    def compare_ptr_helper(t1: PySide6.QtCore.QObject, t2: PySide6.QtCore.QObject, actual: bytes | bytearray | memoryview, expected: bytes | bytearray | memoryview, file: bytes | bytearray | memoryview, line: int, /) -> bool: ...
    @typing.overload
    @staticmethod
    def compare_ptr_helper(t1: int, t2: int, actual: bytes | bytearray | memoryview, expected: bytes | bytearray | memoryview, file: bytes | bytearray | memoryview, line: int, /) -> bool: ...
    @staticmethod
    def compare_string_helper(t1: bytes | bytearray | memoryview, t2: bytes | bytearray | memoryview, actual: bytes | bytearray | memoryview, expected: bytes | bytearray | memoryview, file: bytes | bytearray | memoryview, line: int, /) -> bool: ...
    @staticmethod
    def createTouchDevice(devType: PySide6.QtGui.QInputDevice.DeviceType = ..., caps: PySide6.QtGui.QInputDevice.Capability = ...) -> PySide6.QtGui.QPointingDevice: ...
    @staticmethod
    def currentAppName() -> bytes | bytearray | memoryview: ...
    @staticmethod
    def currentDataTag() -> bytes | bytearray | memoryview: ...
    @staticmethod
    def currentTestFailed() -> bool: ...
    @staticmethod
    def currentTestFunction() -> bytes | bytearray | memoryview: ...
    @staticmethod
    def currentTestResolved() -> bool: ...
    @typing.overload
    @staticmethod
    def failOnWarning() -> None: ...
    @typing.overload
    @staticmethod
    def failOnWarning(messagePattern: PySide6.QtCore.QRegularExpression | str, /) -> None: ...
    @typing.overload
    @staticmethod
    def failOnWarning(message: bytes | bytearray | memoryview, /) -> None: ...
    @staticmethod
    def formatString(prefix: bytes | bytearray | memoryview, suffix: bytes | bytearray | memoryview, numArguments: int, /) -> bytes | bytearray | memoryview: ...
    @typing.overload
    @staticmethod
    def ignoreMessage(type: PySide6.QtCore.QtMsgType, messagePattern: PySide6.QtCore.QRegularExpression | str, /) -> None: ...
    @typing.overload
    @staticmethod
    def ignoreMessage(type: PySide6.QtCore.QtMsgType, message: bytes | bytearray | memoryview, /) -> None: ...
    @typing.overload
    @staticmethod
    def keyClick(widget: PySide6.QtWidgets.QWidget, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyClick(widget: PySide6.QtWidgets.QWidget, key: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyClick(window: PySide6.QtGui.QWindow, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyClick(window: PySide6.QtGui.QWindow, key: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @staticmethod
    def keyClicks(widget: PySide6.QtWidgets.QWidget, sequence: str, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyEvent(action: PySide6.QtTest.QTest.KeyAction, widget: PySide6.QtWidgets.QWidget, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyEvent(action: PySide6.QtTest.QTest.KeyAction, widget: PySide6.QtWidgets.QWidget, ascii: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyEvent(action: PySide6.QtTest.QTest.KeyAction, window: PySide6.QtGui.QWindow, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyEvent(action: PySide6.QtTest.QTest.KeyAction, window: PySide6.QtGui.QWindow, ascii: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyPress(widget: PySide6.QtWidgets.QWidget, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyPress(widget: PySide6.QtWidgets.QWidget, key: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyPress(window: PySide6.QtGui.QWindow, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyPress(window: PySide6.QtGui.QWindow, key: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyRelease(widget: PySide6.QtWidgets.QWidget, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyRelease(widget: PySide6.QtWidgets.QWidget, key: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyRelease(window: PySide6.QtGui.QWindow, key: PySide6.QtCore.Qt.Key, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keyRelease(window: PySide6.QtGui.QWindow, key: int, /, modifier: PySide6.QtCore.Qt.KeyboardModifier = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def keySequence(widget: PySide6.QtWidgets.QWidget, keySequence: PySide6.QtGui.QKeySequence | PySide6.QtCore.QKeyCombination | PySide6.QtGui.QKeySequence.StandardKey | str | int, /) -> None: ...
    @typing.overload
    @staticmethod
    def keySequence(window: PySide6.QtGui.QWindow, keySequence: PySide6.QtGui.QKeySequence | PySide6.QtCore.QKeyCombination | PySide6.QtGui.QKeySequence.StandardKey | str | int, /) -> None: ...
    @staticmethod
    def keyToAscii(key: PySide6.QtCore.Qt.Key, /) -> int: ...
    @typing.overload
    @staticmethod
    def mouseClick(widget: PySide6.QtWidgets.QWidget, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseClick(window: PySide6.QtGui.QWindow, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseDClick(widget: PySide6.QtWidgets.QWidget, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseDClick(window: PySide6.QtGui.QWindow, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseEvent(action: PySide6.QtTest.QTest.MouseAction, widget: PySide6.QtWidgets.QWidget, button: PySide6.QtCore.Qt.MouseButton, stateKey: PySide6.QtCore.Qt.KeyboardModifier, pos: PySide6.QtCore.QPoint, /, delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseEvent(action: PySide6.QtTest.QTest.MouseAction, window: PySide6.QtGui.QWindow, button: PySide6.QtCore.Qt.MouseButton, stateKey: PySide6.QtCore.Qt.KeyboardModifier, pos: PySide6.QtCore.QPoint, /, delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseMove(widget: PySide6.QtWidgets.QWidget, /, pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseMove(window: PySide6.QtGui.QWindow, /, pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mousePress(widget: PySide6.QtWidgets.QWidget, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mousePress(window: PySide6.QtGui.QWindow, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseRelease(widget: PySide6.QtWidgets.QWidget, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def mouseRelease(window: PySide6.QtGui.QWindow, button: PySide6.QtCore.Qt.MouseButton, /, stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., pos: PySide6.QtCore.QPoint = ..., delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def qCaught(expected: bytes | bytearray | memoryview, what: bytes | bytearray | memoryview, file: bytes | bytearray | memoryview, line: int, /) -> None: ...
    @typing.overload
    @staticmethod
    def qCaught(expected: bytes | bytearray | memoryview, file: bytes | bytearray | memoryview, line: int, /) -> None: ...
    @staticmethod
    def qCleanup() -> None: ...
    @staticmethod
    def qElementData(elementName: bytes | bytearray | memoryview, metaTypeId: int, /) -> int: ...
    @staticmethod
    def qExpectFail(dataIndex: bytes | bytearray | memoryview, comment: bytes | bytearray | memoryview, mode: PySide6.QtTest.QTest.TestFailMode, file: bytes | bytearray | memoryview, line: int, /) -> bool: ...
    @typing.overload
    @staticmethod
    def qFindTestData(basepath: str, /, file: bytes | bytearray | memoryview | None = ..., line: int | None = ..., builddir: bytes | bytearray | memoryview | None = ..., sourcedir: bytes | bytearray | memoryview | None = ...) -> str: ...
    @typing.overload
    @staticmethod
    def qFindTestData(basepath: bytes | bytearray | memoryview, /, file: bytes | bytearray | memoryview | None = ..., line: int | None = ..., builddir: bytes | bytearray | memoryview | None = ..., sourcedir: bytes | bytearray | memoryview | None = ...) -> str: ...
    @staticmethod
    def qGlobalData(tagName: bytes | bytearray | memoryview, typeId: int, /) -> int: ...
    @staticmethod
    def qRun() -> int: ...
    @staticmethod
    def qSkip(message: bytes | bytearray | memoryview, file: bytes | bytearray | memoryview, line: int, /) -> None: ...
    @staticmethod
    def qSleep(ms: int, /) -> None: ...
    @staticmethod
    def qWait(ms: int, /) -> None: ...
    @typing.overload
    @staticmethod
    def qWaitForWindowActive(widget: PySide6.QtWidgets.QWidget, /, timeout: int = ...) -> bool: ...
    @typing.overload
    @staticmethod
    def qWaitForWindowActive(window: PySide6.QtGui.QWindow, /, timeout: int = ...) -> bool: ...
    @typing.overload
    @staticmethod
    def qWaitForWindowExposed(widget: PySide6.QtWidgets.QWidget, /, timeout: int = ...) -> bool: ...
    @typing.overload
    @staticmethod
    def qWaitForWindowExposed(window: PySide6.QtGui.QWindow, /, timeout: int = ...) -> bool: ...
    @typing.overload
    @staticmethod
    def qWaitForWindowFocused(widget: PySide6.QtWidgets.QWidget, /, timeout: PySide6.QtCore.QDeadlineTimer | PySide6.QtCore.QDeadlineTimer.ForeverConstant | int = ...) -> bool: ...
    @typing.overload
    @staticmethod
    def qWaitForWindowFocused(window: PySide6.QtGui.QWindow, /, timeout: PySide6.QtCore.QDeadlineTimer | PySide6.QtCore.QDeadlineTimer.ForeverConstant | int = ...) -> bool: ...
    @staticmethod
    def runningTest() -> bool: ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action: PySide6.QtTest.QTest.KeyAction, widget: PySide6.QtWidgets.QWidget, code: PySide6.QtCore.Qt.Key, text: str, modifier: PySide6.QtCore.Qt.KeyboardModifier, /, delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action: PySide6.QtTest.QTest.KeyAction, widget: PySide6.QtWidgets.QWidget, code: PySide6.QtCore.Qt.Key, ascii: int, modifier: PySide6.QtCore.Qt.KeyboardModifier, /, delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action: PySide6.QtTest.QTest.KeyAction, window: PySide6.QtGui.QWindow, code: PySide6.QtCore.Qt.Key, text: str, modifier: PySide6.QtCore.Qt.KeyboardModifier, /, delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def sendKeyEvent(action: PySide6.QtTest.QTest.KeyAction, window: PySide6.QtGui.QWindow, code: PySide6.QtCore.Qt.Key, ascii: int, modifier: PySide6.QtCore.Qt.KeyboardModifier, /, delay: int = ...) -> None: ...
    @staticmethod
    def setBenchmarkResult(result: float, metric: PySide6.QtTest.QTest.QBenchmarkMetric, /) -> None: ...
    @staticmethod
    def setMainSourcePath(file: bytes | bytearray | memoryview, /, builddir: bytes | bytearray | memoryview | None = ...) -> None: ...
    @staticmethod
    def setThrowOnFail(enable: bool, /) -> None: ...
    @staticmethod
    def setThrowOnSkip(enable: bool, /) -> None: ...
    @typing.overload
    @staticmethod
    def simulateEvent(widget: PySide6.QtWidgets.QWidget, press: bool, code: int, modifier: PySide6.QtCore.Qt.KeyboardModifier, text: str, repeat: bool, /, delay: int = ...) -> None: ...
    @typing.overload
    @staticmethod
    def simulateEvent(window: PySide6.QtGui.QWindow, press: bool, code: int, modifier: PySide6.QtCore.Qt.KeyboardModifier, text: str, repeat: bool, /, delay: int = ...) -> None: ...
    @staticmethod
    def testObject() -> PySide6.QtCore.QObject: ...
    @staticmethod
    def toPrettyCString(unicode: bytes | bytearray | memoryview, length: int, /) -> bytes | bytearray | memoryview: ...
    @typing.overload
    @staticmethod
    def touchEvent(widget: PySide6.QtWidgets.QWidget, device: PySide6.QtGui.QPointingDevice, /, autoCommit: bool = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
    @typing.overload
    @staticmethod
    def touchEvent(window: PySide6.QtGui.QWindow, device: PySide6.QtGui.QPointingDevice, /, autoCommit: bool = ...) -> PySide6.QtTest.QTest.QTouchEventSequence: ...
    @staticmethod
    def wheelEvent(window: PySide6.QtGui.QWindow, pos: PySide6.QtCore.QPointF | PySide6.QtCore.QPoint, angleDelta: PySide6.QtCore.QPoint, /, pixelDelta: PySide6.QtCore.QPoint = ..., stateKey: PySide6.QtCore.Qt.KeyboardModifier = ..., phase: PySide6.QtCore.Qt.ScrollPhase = ...) -> None: ...


# eof
