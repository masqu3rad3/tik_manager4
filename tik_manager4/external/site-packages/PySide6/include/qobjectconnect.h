// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QOBJECTCONNECT_H
#define QOBJECTCONNECT_H

#include "pysidemacros.h"

#include <sbkpython.h>

#include <QtCore/qmetaobject.h>

QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_CLASS(QMetaMethod)

namespace PySide
{

/// Helpers for QObject::connect(): Make a string-based connection
PYSIDE_API QMetaObject::Connection
    qobjectConnect(QObject *source, const char *signal,
               QObject *receiver, const char *slot,
               Qt::ConnectionType type);

/// Helpers for QObject::connect(): Make a connection based on QMetaMethod
PYSIDE_API QMetaObject::Connection
    qobjectConnect(QObject *source, QMetaMethod signal,
                   QObject *receiver, QMetaMethod slot,
                   Qt::ConnectionType type);

/// Helpers for QObject::connect(): Make a connection to a Python callback
PYSIDE_API QMetaObject::Connection
    qobjectConnectCallback(QObject *source, const char *signal,
                           PyObject *callback, Qt::ConnectionType type);

/// Helpers for QObject::connect(): Make a connection to a Python callback and a context object
PYSIDE_API QMetaObject::Connection
    qobjectConnectCallback(QObject *source, const char *signal, QObject *context,
                           PyObject *callback, Qt::ConnectionType type);

/// Helpers for QObject::disconnect(): Disconnect a Python callback
PYSIDE_API bool qobjectDisconnectCallback(QObject *source, const char *signal,
                                          PyObject *callback);

/// Helper for functions that forward arguments to QObject::connect(),
/// for example, QTimer::singleShot().
PYSIDE_API bool callConnect(PyObject *self, const char *signal, PyObject *argument);

} // namespace PySide

#endif // QOBJECTCONNECT_H
