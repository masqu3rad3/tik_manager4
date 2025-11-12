// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLATTACHED_P_H
#define PYSIDEQMLATTACHED_P_H

#include <sbkpython.h>

#include <memory>

namespace PySide::Qml {
struct QmlExtensionInfo;
struct QmlTypeInfo;

void initQmlAttached(PyObject *module);

PySide::Qml::QmlExtensionInfo qmlAttachedInfo(PyTypeObject *t,
                                              const std::shared_ptr<QmlTypeInfo> &info);
} // namespace PySide::Qml

#endif // PYSIDEQMLATTACHED_P_H
