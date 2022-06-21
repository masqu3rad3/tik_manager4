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
PySide2.QtTextToSpeech, except for defaults which are replaced by "...".
"""

# Module PySide2.QtTextToSpeech
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
import PySide2.QtTextToSpeech


class QTextToSpeech(PySide2.QtCore.QObject):
    Ready                    : QTextToSpeech = ... # 0x0
    Speaking                 : QTextToSpeech = ... # 0x1
    Paused                   : QTextToSpeech = ... # 0x2
    BackendError             : QTextToSpeech = ... # 0x3

    class State(object):
        Ready                    : QTextToSpeech.State = ... # 0x0
        Speaking                 : QTextToSpeech.State = ... # 0x1
        Paused                   : QTextToSpeech.State = ... # 0x2
        BackendError             : QTextToSpeech.State = ... # 0x3

    @typing.overload
    def __init__(self, engine:str, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...
    @typing.overload
    def __init__(self, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...

    @staticmethod
    def availableEngines() -> typing.List: ...
    def availableLocales(self) -> typing.List: ...
    def availableVoices(self) -> typing.List: ...
    def locale(self) -> PySide2.QtCore.QLocale: ...
    def pause(self): ...
    def pitch(self) -> float: ...
    def rate(self) -> float: ...
    def resume(self): ...
    def say(self, text:str): ...
    def setLocale(self, locale:PySide2.QtCore.QLocale): ...
    def setPitch(self, pitch:float): ...
    def setRate(self, rate:float): ...
    def setVoice(self, voice:PySide2.QtTextToSpeech.QVoice): ...
    def setVolume(self, volume:float): ...
    def state(self) -> PySide2.QtTextToSpeech.QTextToSpeech.State: ...
    def stop(self): ...
    def voice(self) -> PySide2.QtTextToSpeech.QVoice: ...
    def volume(self) -> float: ...


class QTextToSpeechEngine(PySide2.QtCore.QObject):

    def __init__(self, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...

    def availableLocales(self) -> typing.List: ...
    def availableVoices(self) -> typing.List: ...
    @staticmethod
    def createVoice(name:str, gender:PySide2.QtTextToSpeech.QVoice.Gender, age:PySide2.QtTextToSpeech.QVoice.Age, data:typing.Any) -> PySide2.QtTextToSpeech.QVoice: ...
    def locale(self) -> PySide2.QtCore.QLocale: ...
    def pause(self): ...
    def pitch(self) -> float: ...
    def rate(self) -> float: ...
    def resume(self): ...
    def say(self, text:str): ...
    def setLocale(self, locale:PySide2.QtCore.QLocale) -> bool: ...
    def setPitch(self, pitch:float) -> bool: ...
    def setRate(self, rate:float) -> bool: ...
    def setVoice(self, voice:PySide2.QtTextToSpeech.QVoice) -> bool: ...
    def setVolume(self, volume:float) -> bool: ...
    def state(self) -> PySide2.QtTextToSpeech.QTextToSpeech.State: ...
    def stop(self): ...
    def voice(self) -> PySide2.QtTextToSpeech.QVoice: ...
    @staticmethod
    def voiceData(voice:PySide2.QtTextToSpeech.QVoice) -> typing.Any: ...
    def volume(self) -> float: ...


class QVoice(Shiboken.Object):
    Child                    : QVoice = ... # 0x0
    Male                     : QVoice = ... # 0x0
    Female                   : QVoice = ... # 0x1
    Teenager                 : QVoice = ... # 0x1
    Adult                    : QVoice = ... # 0x2
    Unknown                  : QVoice = ... # 0x2
    Senior                   : QVoice = ... # 0x3
    Other                    : QVoice = ... # 0x4

    class Age(object):
        Child                    : QVoice.Age = ... # 0x0
        Teenager                 : QVoice.Age = ... # 0x1
        Adult                    : QVoice.Age = ... # 0x2
        Senior                   : QVoice.Age = ... # 0x3
        Other                    : QVoice.Age = ... # 0x4

    class Gender(object):
        Male                     : QVoice.Gender = ... # 0x0
        Female                   : QVoice.Gender = ... # 0x1
        Unknown                  : QVoice.Gender = ... # 0x2

    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, other:PySide2.QtTextToSpeech.QVoice): ...

    def __copy__(self): ...
    def age(self) -> PySide2.QtTextToSpeech.QVoice.Age: ...
    @staticmethod
    def ageName(age:PySide2.QtTextToSpeech.QVoice.Age) -> str: ...
    def gender(self) -> PySide2.QtTextToSpeech.QVoice.Gender: ...
    @staticmethod
    def genderName(gender:PySide2.QtTextToSpeech.QVoice.Gender) -> str: ...
    def name(self) -> str: ...

# eof
