// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_DYNAMIC_CLASS_P_H
#define PYSIDE_DYNAMIC_CLASS_P_H

#include <sbkpython.h>

#include <QtCore/qtclasshelpermacros.h>

QT_FORWARD_DECLARE_STRUCT(QMetaObject)

PyTypeObject *createDynamicClass(QMetaObject *meta, PyObject *properties_capsule);

#endif // PYSIDE_DYNAMIC_CLASS_P_H
