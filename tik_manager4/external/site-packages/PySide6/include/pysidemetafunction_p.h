// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_METAFUNCTION_P_H
#define PYSIDE_METAFUNCTION_P_H

#include <sbkpython.h>

#include <QtCore/qtconfigmacros.h>

QT_BEGIN_NAMESPACE
class QObject;
QT_END_NAMESPACE

namespace PySide::MetaFunction {

    void init(PyObject *module);
    /**
     * Does a Qt metacall on a QObject
     */
    bool call(QObject *self, int methodIndex, PyObject *args, PyObject **retVal = nullptr);

} //namespace PySide::MetaFunction

#endif
