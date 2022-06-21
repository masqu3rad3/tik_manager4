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
PySide2.QtSerialPort, except for defaults which are replaced by "...".
"""

# Module PySide2.QtSerialPort
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
import PySide2.QtSerialPort


class QSerialPort(PySide2.QtCore.QIODevice):
    UnknownBaud              : QSerialPort = ... # -0x1
    UnknownDataBits          : QSerialPort = ... # -0x1
    UnknownFlowControl       : QSerialPort = ... # -0x1
    UnknownParity            : QSerialPort = ... # -0x1
    UnknownPolicy            : QSerialPort = ... # -0x1
    UnknownStopBits          : QSerialPort = ... # -0x1
    NoError                  : QSerialPort = ... # 0x0
    NoFlowControl            : QSerialPort = ... # 0x0
    NoParity                 : QSerialPort = ... # 0x0
    NoSignal                 : QSerialPort = ... # 0x0
    SkipPolicy               : QSerialPort = ... # 0x0
    DeviceNotFoundError      : QSerialPort = ... # 0x1
    HardwareControl          : QSerialPort = ... # 0x1
    Input                    : QSerialPort = ... # 0x1
    OneStop                  : QSerialPort = ... # 0x1
    PassZeroPolicy           : QSerialPort = ... # 0x1
    TransmittedDataSignal    : QSerialPort = ... # 0x1
    EvenParity               : QSerialPort = ... # 0x2
    IgnorePolicy             : QSerialPort = ... # 0x2
    Output                   : QSerialPort = ... # 0x2
    PermissionError          : QSerialPort = ... # 0x2
    ReceivedDataSignal       : QSerialPort = ... # 0x2
    SoftwareControl          : QSerialPort = ... # 0x2
    TwoStop                  : QSerialPort = ... # 0x2
    AllDirections            : QSerialPort = ... # 0x3
    OddParity                : QSerialPort = ... # 0x3
    OneAndHalfStop           : QSerialPort = ... # 0x3
    OpenError                : QSerialPort = ... # 0x3
    StopReceivingPolicy      : QSerialPort = ... # 0x3
    DataTerminalReadySignal  : QSerialPort = ... # 0x4
    ParityError              : QSerialPort = ... # 0x4
    SpaceParity              : QSerialPort = ... # 0x4
    Data5                    : QSerialPort = ... # 0x5
    FramingError             : QSerialPort = ... # 0x5
    MarkParity               : QSerialPort = ... # 0x5
    BreakConditionError      : QSerialPort = ... # 0x6
    Data6                    : QSerialPort = ... # 0x6
    Data7                    : QSerialPort = ... # 0x7
    WriteError               : QSerialPort = ... # 0x7
    Data8                    : QSerialPort = ... # 0x8
    DataCarrierDetectSignal  : QSerialPort = ... # 0x8
    ReadError                : QSerialPort = ... # 0x8
    ResourceError            : QSerialPort = ... # 0x9
    UnsupportedOperationError: QSerialPort = ... # 0xa
    UnknownError             : QSerialPort = ... # 0xb
    TimeoutError             : QSerialPort = ... # 0xc
    NotOpenError             : QSerialPort = ... # 0xd
    DataSetReadySignal       : QSerialPort = ... # 0x10
    RingIndicatorSignal      : QSerialPort = ... # 0x20
    RequestToSendSignal      : QSerialPort = ... # 0x40
    ClearToSendSignal        : QSerialPort = ... # 0x80
    SecondaryTransmittedDataSignal: QSerialPort = ... # 0x100
    SecondaryReceivedDataSignal: QSerialPort = ... # 0x200
    Baud1200                 : QSerialPort = ... # 0x4b0
    Baud2400                 : QSerialPort = ... # 0x960
    Baud4800                 : QSerialPort = ... # 0x12c0
    Baud9600                 : QSerialPort = ... # 0x2580
    Baud19200                : QSerialPort = ... # 0x4b00
    Baud38400                : QSerialPort = ... # 0x9600
    Baud57600                : QSerialPort = ... # 0xe100
    Baud115200               : QSerialPort = ... # 0x1c200

    class BaudRate(object):
        UnknownBaud              : QSerialPort.BaudRate = ... # -0x1
        Baud1200                 : QSerialPort.BaudRate = ... # 0x4b0
        Baud2400                 : QSerialPort.BaudRate = ... # 0x960
        Baud4800                 : QSerialPort.BaudRate = ... # 0x12c0
        Baud9600                 : QSerialPort.BaudRate = ... # 0x2580
        Baud19200                : QSerialPort.BaudRate = ... # 0x4b00
        Baud38400                : QSerialPort.BaudRate = ... # 0x9600
        Baud57600                : QSerialPort.BaudRate = ... # 0xe100
        Baud115200               : QSerialPort.BaudRate = ... # 0x1c200

    class DataBits(object):
        UnknownDataBits          : QSerialPort.DataBits = ... # -0x1
        Data5                    : QSerialPort.DataBits = ... # 0x5
        Data6                    : QSerialPort.DataBits = ... # 0x6
        Data7                    : QSerialPort.DataBits = ... # 0x7
        Data8                    : QSerialPort.DataBits = ... # 0x8

    class DataErrorPolicy(object):
        UnknownPolicy            : QSerialPort.DataErrorPolicy = ... # -0x1
        SkipPolicy               : QSerialPort.DataErrorPolicy = ... # 0x0
        PassZeroPolicy           : QSerialPort.DataErrorPolicy = ... # 0x1
        IgnorePolicy             : QSerialPort.DataErrorPolicy = ... # 0x2
        StopReceivingPolicy      : QSerialPort.DataErrorPolicy = ... # 0x3

    class Direction(object):
        Input                    : QSerialPort.Direction = ... # 0x1
        Output                   : QSerialPort.Direction = ... # 0x2
        AllDirections            : QSerialPort.Direction = ... # 0x3

    class Directions(object): ...

    class FlowControl(object):
        UnknownFlowControl       : QSerialPort.FlowControl = ... # -0x1
        NoFlowControl            : QSerialPort.FlowControl = ... # 0x0
        HardwareControl          : QSerialPort.FlowControl = ... # 0x1
        SoftwareControl          : QSerialPort.FlowControl = ... # 0x2

    class Parity(object):
        UnknownParity            : QSerialPort.Parity = ... # -0x1
        NoParity                 : QSerialPort.Parity = ... # 0x0
        EvenParity               : QSerialPort.Parity = ... # 0x2
        OddParity                : QSerialPort.Parity = ... # 0x3
        SpaceParity              : QSerialPort.Parity = ... # 0x4
        MarkParity               : QSerialPort.Parity = ... # 0x5

    class PinoutSignal(object):
        NoSignal                 : QSerialPort.PinoutSignal = ... # 0x0
        TransmittedDataSignal    : QSerialPort.PinoutSignal = ... # 0x1
        ReceivedDataSignal       : QSerialPort.PinoutSignal = ... # 0x2
        DataTerminalReadySignal  : QSerialPort.PinoutSignal = ... # 0x4
        DataCarrierDetectSignal  : QSerialPort.PinoutSignal = ... # 0x8
        DataSetReadySignal       : QSerialPort.PinoutSignal = ... # 0x10
        RingIndicatorSignal      : QSerialPort.PinoutSignal = ... # 0x20
        RequestToSendSignal      : QSerialPort.PinoutSignal = ... # 0x40
        ClearToSendSignal        : QSerialPort.PinoutSignal = ... # 0x80
        SecondaryTransmittedDataSignal: QSerialPort.PinoutSignal = ... # 0x100
        SecondaryReceivedDataSignal: QSerialPort.PinoutSignal = ... # 0x200

    class PinoutSignals(object): ...

    class SerialPortError(object):
        NoError                  : QSerialPort.SerialPortError = ... # 0x0
        DeviceNotFoundError      : QSerialPort.SerialPortError = ... # 0x1
        PermissionError          : QSerialPort.SerialPortError = ... # 0x2
        OpenError                : QSerialPort.SerialPortError = ... # 0x3
        ParityError              : QSerialPort.SerialPortError = ... # 0x4
        FramingError             : QSerialPort.SerialPortError = ... # 0x5
        BreakConditionError      : QSerialPort.SerialPortError = ... # 0x6
        WriteError               : QSerialPort.SerialPortError = ... # 0x7
        ReadError                : QSerialPort.SerialPortError = ... # 0x8
        ResourceError            : QSerialPort.SerialPortError = ... # 0x9
        UnsupportedOperationError: QSerialPort.SerialPortError = ... # 0xa
        UnknownError             : QSerialPort.SerialPortError = ... # 0xb
        TimeoutError             : QSerialPort.SerialPortError = ... # 0xc
        NotOpenError             : QSerialPort.SerialPortError = ... # 0xd

    class StopBits(object):
        UnknownStopBits          : QSerialPort.StopBits = ... # -0x1
        OneStop                  : QSerialPort.StopBits = ... # 0x1
        TwoStop                  : QSerialPort.StopBits = ... # 0x2
        OneAndHalfStop           : QSerialPort.StopBits = ... # 0x3

    @typing.overload
    def __init__(self, info:PySide2.QtSerialPort.QSerialPortInfo, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...
    @typing.overload
    def __init__(self, name:str, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...
    @typing.overload
    def __init__(self, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...

    def atEnd(self) -> bool: ...
    def baudRate(self, directions:PySide2.QtSerialPort.QSerialPort.Directions=...) -> int: ...
    def bytesAvailable(self) -> int: ...
    def bytesToWrite(self) -> int: ...
    def canReadLine(self) -> bool: ...
    def clear(self, directions:PySide2.QtSerialPort.QSerialPort.Directions=...) -> bool: ...
    def clearError(self): ...
    def close(self): ...
    def dataBits(self) -> PySide2.QtSerialPort.QSerialPort.DataBits: ...
    def dataErrorPolicy(self) -> PySide2.QtSerialPort.QSerialPort.DataErrorPolicy: ...
    def error(self) -> PySide2.QtSerialPort.QSerialPort.SerialPortError: ...
    def flowControl(self) -> PySide2.QtSerialPort.QSerialPort.FlowControl: ...
    def flush(self) -> bool: ...
    def handle(self) -> int: ...
    def isBreakEnabled(self) -> bool: ...
    def isDataTerminalReady(self) -> bool: ...
    def isRequestToSend(self) -> bool: ...
    def isSequential(self) -> bool: ...
    def open(self, mode:PySide2.QtCore.QIODevice.OpenMode) -> bool: ...
    def parity(self) -> PySide2.QtSerialPort.QSerialPort.Parity: ...
    def pinoutSignals(self) -> PySide2.QtSerialPort.QSerialPort.PinoutSignals: ...
    def portName(self) -> str: ...
    def readBufferSize(self) -> int: ...
    def readData(self, data:bytes, maxSize:int) -> int: ...
    def readLineData(self, data:bytes, maxSize:int) -> int: ...
    def sendBreak(self, duration:int=...) -> bool: ...
    def setBaudRate(self, baudRate:int, directions:PySide2.QtSerialPort.QSerialPort.Directions=...) -> bool: ...
    def setBreakEnabled(self, set:bool=...) -> bool: ...
    def setDataBits(self, dataBits:PySide2.QtSerialPort.QSerialPort.DataBits) -> bool: ...
    def setDataErrorPolicy(self, policy:PySide2.QtSerialPort.QSerialPort.DataErrorPolicy=...) -> bool: ...
    def setDataTerminalReady(self, set:bool) -> bool: ...
    def setFlowControl(self, flowControl:PySide2.QtSerialPort.QSerialPort.FlowControl) -> bool: ...
    def setParity(self, parity:PySide2.QtSerialPort.QSerialPort.Parity) -> bool: ...
    def setPort(self, info:PySide2.QtSerialPort.QSerialPortInfo): ...
    def setPortName(self, name:str): ...
    def setReadBufferSize(self, size:int): ...
    def setRequestToSend(self, set:bool) -> bool: ...
    def setSettingsRestoredOnClose(self, restore:bool): ...
    def setStopBits(self, stopBits:PySide2.QtSerialPort.QSerialPort.StopBits) -> bool: ...
    def settingsRestoredOnClose(self) -> bool: ...
    def stopBits(self) -> PySide2.QtSerialPort.QSerialPort.StopBits: ...
    def waitForBytesWritten(self, msecs:int=...) -> bool: ...
    def waitForReadyRead(self, msecs:int=...) -> bool: ...
    def writeData(self, data:bytes, maxSize:int) -> int: ...


class QSerialPortInfo(Shiboken.Object):

    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, name:str): ...
    @typing.overload
    def __init__(self, other:PySide2.QtSerialPort.QSerialPortInfo): ...
    @typing.overload
    def __init__(self, port:PySide2.QtSerialPort.QSerialPort): ...

    def __copy__(self): ...
    @staticmethod
    def availablePorts() -> typing.List: ...
    def description(self) -> str: ...
    def hasProductIdentifier(self) -> bool: ...
    def hasVendorIdentifier(self) -> bool: ...
    def isBusy(self) -> bool: ...
    def isNull(self) -> bool: ...
    def isValid(self) -> bool: ...
    def manufacturer(self) -> str: ...
    def portName(self) -> str: ...
    def productIdentifier(self) -> int: ...
    def serialNumber(self) -> str: ...
    @staticmethod
    def standardBaudRates() -> typing.List: ...
    def swap(self, other:PySide2.QtSerialPort.QSerialPortInfo): ...
    def systemLocation(self) -> str: ...
    def vendorIdentifier(self) -> int: ...

# eof
