// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef FEATURE_SELECT_H
#define FEATURE_SELECT_H

#include "pysidemacros.h"
#include <sbkpython.h>

namespace PySide::Feature {

PYSIDE_API void init();
PYSIDE_API void Select(PyObject *obj);
PYSIDE_API void Select(PyTypeObject *type);
PYSIDE_API void Enable(bool);

} // namespace PySide::Feature

#endif // FEATURE_SELECT_H
