# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""Provides some type information on Qt classes"""


from enum import Flag


class ClassFlag(Flag):
    PASS_BY_CONSTREF = 1
    PASS_BY_REF = 2
    PASS_BY_VALUE = 4
    PASS_ON_STACK_MASK = PASS_BY_CONSTREF | PASS_BY_REF | PASS_BY_VALUE
    INSTANTIATE_ON_STACK = 8


_QT_CLASS_FLAGS = {
    # QtCore
    "QCoreApplication": ClassFlag.INSTANTIATE_ON_STACK,
    "QFile": ClassFlag.PASS_BY_REF | ClassFlag.INSTANTIATE_ON_STACK,
    "QFileInfo": ClassFlag.INSTANTIATE_ON_STACK,
    "QLine": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QLineF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QModelIndex": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QPoint": ClassFlag.PASS_BY_VALUE | ClassFlag.INSTANTIATE_ON_STACK,
    "QPointF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QRect": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QRectF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QSaveFile": ClassFlag.INSTANTIATE_ON_STACK,
    "QSettings": ClassFlag.PASS_BY_REF | ClassFlag.INSTANTIATE_ON_STACK,
    "QSize": ClassFlag.PASS_BY_VALUE | ClassFlag.INSTANTIATE_ON_STACK,
    "QSizeF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QString": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QTextStream": ClassFlag.PASS_BY_REF | ClassFlag.INSTANTIATE_ON_STACK,
    # QtGui
    "QBrush": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QColor": ClassFlag.PASS_BY_VALUE | ClassFlag.INSTANTIATE_ON_STACK,
    "QGradient": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QGuiApplication": ClassFlag.INSTANTIATE_ON_STACK,
    "QIcon": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QPainter": ClassFlag.INSTANTIATE_ON_STACK,
    "QPen": ClassFlag.INSTANTIATE_ON_STACK,
    "QPixmap": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    # QtWidgets
    "QApplication": ClassFlag.INSTANTIATE_ON_STACK,
    "QColorDialog": ClassFlag.INSTANTIATE_ON_STACK,
    "QFileDialog": ClassFlag.INSTANTIATE_ON_STACK,
    "QFontDialog": ClassFlag.INSTANTIATE_ON_STACK,
    "QMessageBox": ClassFlag.INSTANTIATE_ON_STACK,
    # QtQml
    "QQmlApplicationEngine": ClassFlag.INSTANTIATE_ON_STACK,
    "QQmlComponent": ClassFlag.INSTANTIATE_ON_STACK,
    "QQmlEngine": ClassFlag.INSTANTIATE_ON_STACK,
    # QtQuick
    "QQuickView": ClassFlag.INSTANTIATE_ON_STACK
}


def qt_class_flags(type):
    f = _QT_CLASS_FLAGS.get(type)
    return f if f else ClassFlag(0)
