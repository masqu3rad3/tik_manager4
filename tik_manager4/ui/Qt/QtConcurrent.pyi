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
PySide2.QtConcurrent, except for defaults which are replaced by "...".
"""

# Module PySide2.QtConcurrent
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

import PySide2.QtConcurrent


class QtConcurrent(Shiboken.Object):
    ThrottleThread           : QtConcurrent = ... # 0x0
    ThreadFinished           : QtConcurrent = ... # 0x1
    UnorderedReduce          : QtConcurrent = ... # 0x1
    OrderedReduce            : QtConcurrent = ... # 0x2
    SequentialReduce         : QtConcurrent = ... # 0x4

    class ReduceOption(object):
        UnorderedReduce          : QtConcurrent.ReduceOption = ... # 0x1
        OrderedReduce            : QtConcurrent.ReduceOption = ... # 0x2
        SequentialReduce         : QtConcurrent.ReduceOption = ... # 0x4

    class ReduceOptions(object): ...

    class ThreadFunctionResult(object):
        ThrottleThread           : QtConcurrent.ThreadFunctionResult = ... # 0x0
        ThreadFinished           : QtConcurrent.ThreadFunctionResult = ... # 0x1

# eof
