// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQML_H
#define PYSIDEQML_H

#include "pysideqmlmacros.h"

#include <sbkpython.h>

namespace PySide::Qml
{

PYSIDEQML_API void init(PyObject *module);

} //namespace PySide::Qml

#endif // PYSIDEQML_H
