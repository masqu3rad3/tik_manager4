// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLUNCREATABLE_H
#define PYSIDEQMLUNCREATABLE_H

#include <sbkpython.h>

#include <QtCore/qbytearray.h>

QT_FORWARD_DECLARE_CLASS(QMetaObjectBuilder)

// The QmlUncreatable decorator modifies QmlElement to register an uncreatable
// type. Due to the (reverse) execution order of decorators, it needs to follow
// QmlElement.
extern "C"
{
    extern PyTypeObject *PySideQmlUncreatable_TypeF(void);
}

void initQmlUncreatable(PyObject *module);

void setUncreatableClassInfo(PyTypeObject *type, const QByteArray &reason);
void setUncreatableClassInfo(QMetaObjectBuilder *builder, const QByteArray &reason);

#endif // PYSIDEQMLUNCREATABLE_H
