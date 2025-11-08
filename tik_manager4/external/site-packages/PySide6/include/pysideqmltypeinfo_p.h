// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLTYPEINFO_P_H
#define PYSIDEQMLTYPEINFO_P_H

#include <sbkpython.h>

#include <QtCore/qbytearray.h>
#include <QtCore/qflags.h>

#include <memory>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_STRUCT(QMetaObject)

namespace PySide::Qml {

enum class QmlTypeFlag
{
    Singleton = 0x1
};

Q_DECLARE_FLAGS(QmlTypeFlags, QmlTypeFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(QmlTypeFlags)

// Type information associated with QML type objects
struct QmlTypeInfo
{
    QmlTypeFlags flags;
    PyTypeObject *foreignType = nullptr;
    PyTypeObject *attachedType = nullptr;
    PyTypeObject *extensionType = nullptr;
};

using QmlTypeInfoPtr = std::shared_ptr<QmlTypeInfo>;

QmlTypeInfoPtr ensureQmlTypeInfo(const PyObject *o);
void insertQmlTypeInfoAlias(const PyObject *o, const QmlTypeInfoPtr &value);
QmlTypeInfoPtr qmlTypeInfo(const PyObject *o);

// Meta Object and factory function for QmlExtended/QmlAttached
struct QmlExtensionInfo
{
    using Factory = QObject *(*)(QObject *);

    Factory factory;
    const QMetaObject *metaObject;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const QmlTypeInfo &);
QDebug operator<<(QDebug d, const QmlExtensionInfo &);
#endif

} // namespace PySide::Qml

#endif // PYSIDEQMLTYPEINFO_P_H
