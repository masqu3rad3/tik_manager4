// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLFOREIGN_P_H
#define PYSIDEQMLFOREIGN_P_H

#include <sbkpython.h>

namespace PySide::Qml {
struct QmlExtensionInfo;
struct QmlTypeInfo;

void initQmlForeign(PyObject *module);

} // namespace PySide::Qml

#endif // PYSIDEQMLFOREIGN_P_H
