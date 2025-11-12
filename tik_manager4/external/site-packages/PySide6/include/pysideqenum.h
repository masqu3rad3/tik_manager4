// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_QENUM_H
#define PYSIDE_QENUM_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <vector>

namespace PySide::QEnum {

// PYSIDE-957: Support the QEnum macro
PYSIDE_API PyObject *QEnumMacro(PyObject *, bool);
PYSIDE_API int isFlag(PyObject *);
PYSIDE_API std::vector<PyObject *> resolveDelayedQEnums(PyTypeObject *);
PYSIDE_API void init();

} // namespace PySide::QEnum

#endif
