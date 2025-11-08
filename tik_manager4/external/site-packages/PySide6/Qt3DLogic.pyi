# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
"""
This file contains the exact signatures for all functions in module
PySide6.Qt3DLogic, except for defaults which are replaced by "...".

# mypy: disable-error-code="override, overload-overlap"
"""

# Module `PySide6.Qt3DLogic`

import PySide6.Qt3DLogic
import PySide6.QtCore
import PySide6.Qt3DCore

import typing
from PySide6.QtCore import Signal
from shiboken6 import Shiboken


class QIntList: ...


class Qt3DLogic(Shiboken.Object):

    class QFrameAction(PySide6.Qt3DCore.Qt3DCore.QComponent):

        triggered                : typing.ClassVar[Signal] = ... # triggered(float)

        def __init__(self, /, parent: PySide6.Qt3DCore.Qt3DCore.QNode | None = ...) -> None: ...


    class QLogicAspect(PySide6.Qt3DCore.Qt3DCore.QAbstractAspect):

        def __init__(self, /, parent: PySide6.QtCore.QObject | None = ...) -> None: ...


# eof
